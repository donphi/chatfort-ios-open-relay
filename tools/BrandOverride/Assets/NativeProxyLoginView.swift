import SwiftUI

// MARK: - Native Proxy Login View (ChatFort Override)

/// Native SwiftUI login form for Authentik Flow Executor authentication.
/// Replaces the WKWebView-based ProxyAuthView for Authentik servers.
struct NativeProxyLoginView: View {
    @Bindable var viewModel: AuthViewModel
    @Environment(\.theme) private var theme
    @State private var appeared = false
    @State private var logoScale: CGFloat = 0.5
    @State private var logoOpacity: Double = 0
    @FocusState private var focusedField: NativeLoginField?

    private enum NativeLoginField {
        case username, password, totp
    }

    var body: some View {
        ZStack {
            AnimatedAuthBackground()

            ScrollView(showsIndicators: false) {
                VStack(spacing: Spacing.xl) {
                    Spacer(minLength: 50)

                    // App branding
                    VStack(spacing: Spacing.md) {
                        ZStack {
                            Circle()
                                .fill(Color.clear)
                                .frame(width: 100, height: 100)
                                .scaleEffect(logoScale * 1.3)

                            Circle()
                                .fill(Color.clear)
                                .frame(width: 130, height: 130)
                                .scaleEffect(logoScale * 1.1)

                            Image("AppIconImage")
                                .resizable()
                                .scaledToFill()
                                .frame(width: 100, height: 100)
                                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                                .scaleEffect(logoScale)
                        }
                        .opacity(logoOpacity)

                        Text("ChatFort")
                            .scaledFont(size: 36, weight: .bold, design: .rounded)
                            .foregroundStyle(theme.textPrimary)
                            .opacity(appeared ? 1 : 0)
                            .offset(y: appeared ? 0 : 10)

                        Text("Sign in to continue")
                            .scaledFont(size: 16)
                            .foregroundStyle(theme.textSecondary)
                            .opacity(appeared ? 1 : 0)
                            .offset(y: appeared ? 0 : 10)
                    }

                    // Login form card
                    VStack(spacing: Spacing.lg) {
                        if viewModel.nativeProxyNeedsMFA {
                            mfaForm
                        } else {
                            loginForm
                        }

                        if let error = viewModel.errorMessage {
                            HStack(spacing: Spacing.sm) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .foregroundStyle(theme.error)
                                Text(error)
                                    .scaledFont(size: 12, weight: .medium)
                                    .foregroundStyle(theme.error)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(Spacing.md)
                            .background(theme.errorBackground)
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.md, style: .continuous))
                        }
                    }
                    .padding(Spacing.lg)
                    .background(theme.surfaceContainer)
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.xl, style: .continuous))
                    .shadow(color: .black.opacity(0.08), radius: 20, y: 10)

                    Spacer(minLength: 30)
                }
                .padding(.horizontal, Spacing.lg)
            }
        }
        .onAppear {
            withAnimation(.spring(response: 0.6, dampingFraction: 0.7).delay(0.1)) {
                logoScale = 1.0
                logoOpacity = 1.0
            }
            withAnimation(.spring(response: 0.5, dampingFraction: 0.8).delay(0.3)) {
                appeared = true
            }
        }
    }

    // MARK: - Login Form

    @ViewBuilder
    private var loginForm: some View {
        ModernTextField(
            label: "Email",
            placeholder: "Enter your email",
            text: $viewModel.nativeProxyUsername,
            keyboardType: .emailAddress,
            textContentType: .emailAddress,
            onSubmit: { focusedField = .password }
        )
        .focused($focusedField, equals: .username)

        ModernTextField(
            label: "Password",
            placeholder: "Enter your password",
            text: $viewModel.nativeProxyPassword,
            isSecure: true,
            textContentType: .password,
            onSubmit: { submitLogin() }
        )
        .focused($focusedField, equals: .password)

        AuthPrimaryButton(
            title: viewModel.isNativeProxyLoggingIn ? "Signing in..." : "Sign In",
            icon: viewModel.isNativeProxyLoggingIn ? nil : "arrow.right",
            isLoading: viewModel.isNativeProxyLoggingIn,
            isDisabled: viewModel.nativeProxyUsername.isEmpty || viewModel.nativeProxyPassword.isEmpty
        ) {
            submitLogin()
        }
    }

    // MARK: - MFA Form

    @ViewBuilder
    private var mfaForm: some View {
        VStack(spacing: Spacing.md) {
            Image(systemName: "lock.shield")
                .scaledFont(size: 40)
                .foregroundStyle(theme.brandPrimary)

            Text("Two-Factor Authentication")
                .scaledFont(size: 20, weight: .semibold)
                .foregroundStyle(theme.textPrimary)

            Text("Enter the code from your authenticator app")
                .scaledFont(size: 14)
                .foregroundStyle(theme.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding(.bottom, Spacing.md)

        ModernTextField(
            label: "Verification Code",
            placeholder: "000000",
            text: $viewModel.nativeProxyTOTP,
            keyboardType: .numberPad,
            textContentType: .oneTimeCode,
            onSubmit: { submitMFA() }
        )
        .focused($focusedField, equals: .totp)

        AuthPrimaryButton(
            title: viewModel.isNativeProxyLoggingIn ? "Verifying..." : "Verify",
            icon: viewModel.isNativeProxyLoggingIn ? nil : "checkmark.shield",
            isLoading: viewModel.isNativeProxyLoggingIn,
            isDisabled: viewModel.nativeProxyTOTP.isEmpty
        ) {
            submitMFA()
        }
    }

    // MARK: - Actions

    private func submitLogin() {
        guard !viewModel.nativeProxyUsername.isEmpty,
              !viewModel.nativeProxyPassword.isEmpty else { return }
        Task { await viewModel.authenticateViaFlowExecutor() }
    }

    private func submitMFA() {
        guard !viewModel.nativeProxyTOTP.isEmpty else { return }
        Task { await viewModel.submitNativeProxyMFA() }
    }
}
