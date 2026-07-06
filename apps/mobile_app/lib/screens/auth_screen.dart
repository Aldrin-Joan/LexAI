import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/l10n/app_localizations.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/language_provider.dart';
import 'package:flutter_application_1/providers/auth_ui_controller.dart';
import 'package:flutter_application_1/providers/theme_provider.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:flutter_application_1/widgets/gradient_button.dart';

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({super.key});

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen> {
  bool _obscure = true;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final state = ref.watch(authUiProvider);
    final controller = ref.read(authUiProvider.notifier);
    final isLogin = state.mode == AuthMode.login;
    final themeMode = ref.watch(themeModeProvider);
    final isDark = themeMode == ThemeMode.dark;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isDark
                ? [const Color(0xFF1F2937), const Color(0xFF111827)]
                : [const Color(0xFFE0EAFC), const Color(0xFFCFDEF3)],
          ),
        ),
        child: SafeArea(
          child: Stack(
            children: [
              /// Theme Toggle (Top Left)
              Positioned(
                top: 20,
                left: 20,
                child: IconButton(
                  icon: Icon(
                    isDark ? Icons.light_mode : Icons.dark_mode,
                    color: isDark ? Colors.white : Colors.black,
                  ),
                  onPressed: () {
                    ref.read(themeModeProvider.notifier).toggle();
                  },
                ),
              ),

              /// Language Selector
              const Positioned(
                top: 20,
                right: 20,
                child: LanguageSelector(),
              ),

              Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: Container(
                      padding: const EdgeInsets.all(36),
                      decoration: BoxDecoration(
                        color: isDark
                            ? Colors.white.withOpacity(0.05)
                            : Colors.white,
                        borderRadius: BorderRadius.circular(28),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            "LAWGiX",
                            style: GoogleFonts.sora(
                              fontSize: 30,
                              fontWeight: FontWeight.bold,
                              color:
                                  isDark ? Colors.white : Colors.black,
                            ),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            l10n.welcomeMessage,
                            textAlign: TextAlign.center,
                            style: GoogleFonts.sora(
                              fontSize: 16,
                              color: isDark
                                  ? Colors.white70
                                  : Colors.black54,
                            ),
                          ),
                          const SizedBox(height: 28),

                          /// Email
                          _inputField(
                            label: l10n.email,
                            icon: Icons.email_outlined,
                            isDark: isDark,
                          ),

                          const SizedBox(height: 16),

                          /// Full Name
                          if (!isLogin) ...[
                            _inputField(
                              label: l10n.fullName,
                              icon: Icons.person_outline,
                              isDark: isDark,
                            ),
                            const SizedBox(height: 16),
                          ],

                          /// Password with toggle
                          TextField(
                            obscureText: _obscure,
                            style: TextStyle(
                                color:
                                    isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              labelText: l10n.password,
                              prefixIcon: Icon(Icons.lock_outline,
                                  color: isDark
                                      ? Colors.white70
                                      : Colors.black54),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscure
                                      ? Icons.visibility_off
                                      : Icons.visibility,
                                  color: isDark
                                      ? Colors.white70
                                      : Colors.black54,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscure = !_obscure;
                                  });
                                },
                              ),
                              filled: true,
                              fillColor: isDark
                                  ? Colors.white.withOpacity(0.08)
                                  : Colors.grey.shade200,
                              border: OutlineInputBorder(
                                borderRadius:
                                    BorderRadius.circular(16),
                                borderSide: BorderSide.none,
                              ),
                            ),
                          ),

                          const SizedBox(height: 28),
                          /// ⭐ Role Selector (Client / Lawyer)
Container(
  padding: const EdgeInsets.all(4),
  decoration: BoxDecoration(
    color: isDark
        ? Colors.white.withOpacity(0.08)
        : Colors.grey.shade200,
    borderRadius: BorderRadius.circular(14),
  ),
  child: Row(
    children: [
      Expanded(
        child: GestureDetector(
          onTap: () => controller.selectRole(UserRole.client),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: state.role == UserRole.client
                  ? AppColors.primary
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(10),
            ),
            alignment: Alignment.center,
            child: Text(
              "Client",
              style: GoogleFonts.sora(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: state.role == UserRole.client
                    ? Colors.white
                    : (isDark ? Colors.white70 : Colors.black54),
              ),
            ),
          ),
        ),
      ),
      Expanded(
        child: GestureDetector(
          onTap: () => controller.selectRole(UserRole.lawyer),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: state.role == UserRole.lawyer
                  ? AppColors.primary
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(10),
            ),
            alignment: Alignment.center,
            child: Text(
              "Lawyer",
              style: GoogleFonts.sora(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: state.role == UserRole.lawyer
                    ? Colors.white
                    : (isDark ? Colors.white70 : Colors.black54),
              ),
            ),
          ),
        ),
      ),
    ],
  ),
),
const SizedBox(height: 20),
                          /// Button
                          GradientButton(
                            text: isLogin
                                ? l10n.login
                                : l10n.signup,
                            onPressed: () {
                              context.go(
                                state.role == UserRole.client
                                    ? '/client'
                                    : '/lawyer',
                              );
                            },
                          ),

                          const SizedBox(height: 20),

                          Row(
                            mainAxisAlignment:
                                MainAxisAlignment.center,
                            children: [
                              Text(
                                isLogin
                                    ? "Don't have an account? "
                                    : "Already have an account? ",
                                style: TextStyle(
                                  color: isDark
                                      ? Colors.white60
                                      : Colors.black54,
                                ),
                              ),
                              GestureDetector(
                                onTap: controller.toggleMode,
                                child: Text(
                                  isLogin
                                      ? l10n.signup
                                      : l10n.login,
                                  style: GoogleFonts.sora(
                                    color: AppColors.primary,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _inputField({
    required String label,
    required IconData icon,
    required bool isDark,
  }) {
    return TextField(
      style: TextStyle(
          color: isDark ? Colors.white : Colors.black),
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon,
            color: isDark ? Colors.white70 : Colors.black54),
        filled: true,
        fillColor: isDark
            ? Colors.white.withOpacity(0.08)
            : Colors.grey.shade200,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
      ),
    );
  }
}