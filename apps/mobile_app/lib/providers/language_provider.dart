import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:google_fonts/google_fonts.dart';

/// ------------------------------
/// Locale State (Riverpod)
/// ------------------------------
class LocaleNotifier extends Notifier<Locale> {
  @override
  Locale build() => const Locale('en');

  void update(Locale locale) {
    if (state != locale) {
      state = locale;
    }
  }
}

final localeProvider = NotifierProvider<LocaleNotifier, Locale>(
  LocaleNotifier.new,
);

/// ------------------------------
/// Language Model
/// ------------------------------
@immutable
class AppLanguage {
  final Locale locale;
  final String label;

  const AppLanguage(this.locale, this.label);
}

const supportedLanguages = <AppLanguage>[
  AppLanguage(Locale('en'), 'English'),
  AppLanguage(Locale('ta'), 'தமிழ் (Tamil)'),
  AppLanguage(Locale('hi'), 'हिन्दी (Hindi)'),
  AppLanguage(Locale('ml'), 'മലയാളം (Malayalam)'),
  AppLanguage(Locale('kn'), 'ಕನ್ನಡ (Kannada)'),
  AppLanguage(Locale('te'), 'తెలుగు (Telugu)'),
];

/// ------------------------------
/// Language Selector (Custom Popup)
/// ------------------------------
class LanguageSelector extends ConsumerWidget {
  const LanguageSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentLocale = ref.watch(localeProvider);
    final currentLang = supportedLanguages.firstWhere(
      (l) => l.locale == currentLocale,
      orElse: () => supportedLanguages.first,
    );

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceLight,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.5), width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Theme(
        data: Theme.of(context).copyWith(
          splashColor: Colors.transparent,
          highlightColor: Colors.transparent,
        ),
        child: PopupMenuButton<Locale>(
          initialValue: currentLocale,
          tooltip: 'Select Language',
          elevation: 8,
          shadowColor: Colors.black.withOpacity(0.2),
          surfaceTintColor: Colors.white,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          offset: const Offset(0, 48),
          onSelected: (locale) {
            ref.read(localeProvider.notifier).update(locale);
          },
          itemBuilder: (context) => supportedLanguages.map((lang) {
            final isSelected = currentLocale == lang.locale;
            return PopupMenuItem(
              value: lang.locale,
              height: 48,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  color: isSelected
                      ? AppColors.primary.withOpacity(0.05)
                      : Colors.transparent,
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        lang.label,
                        style: GoogleFonts.sora(
                          fontSize: 14,
                          fontWeight: isSelected
                              ? FontWeight.w600
                              : FontWeight.w500,
                          color: isSelected
                              ? AppColors.primary
                              : AppColors.textPrimaryLight,
                        ),
                      ),
                    ),
                    if (isSelected)
                      const Icon(
                        Icons.check_rounded,
                        color: AppColors.primary,
                        size: 18,
                      ),
                  ],
                ),
              ),
            );
          }).toList(),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.language_rounded,
                  size: 18,
                  color: AppColors.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  currentLang.label,
                  style: GoogleFonts.sora(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimaryLight,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(
                  Icons.keyboard_arrow_down_rounded,
                  size: 18,
                  color: AppColors.textSecondaryLight,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
