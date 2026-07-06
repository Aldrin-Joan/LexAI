import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:flutter_application_1/screens/lawyer/edit_profile_screen.dart';
import 'package:flutter_application_1/screens/lawyer/my_clients_screen.dart';
import 'package:flutter_application_1/screens/lawyer/lawyer_availability_screen.dart';

import 'package:flutter_application_1/l10n/app_localizations.dart';
import 'package:flutter_application_1/providers/language_provider.dart';
import 'package:flutter_application_1/providers/theme_provider.dart';
import 'package:flutter_application_1/theme/app_colors.dart';

/// SCREENS
import 'package:flutter_application_1/screens/auth_screen.dart';
import 'package:flutter_application_1/screens/client_dashboard.dart';
import 'package:flutter_application_1/screens/lawyer_dashboard.dart';
import 'package:flutter_application_1/screens/lawyer_profile_screen.dart';
import 'package:flutter_application_1/screens/ai_chat_screen.dart';
import 'package:flutter_application_1/screens/upload_screen.dart';
import 'package:flutter_application_1/screens/find_lawyers_screen.dart';
import 'package:flutter_application_1/screens/profile_screen.dart';
import 'package:flutter_application_1/screens/lawyer_chat_screen.dart';
import 'package:flutter_application_1/screens/payment_method.dart';
import 'package:flutter_application_1/screens/notification_screen.dart';
import 'package:flutter_application_1/screens/help_support_screen.dart';
import 'package:flutter_application_1/screens/privacy_security_screen.dart';
import 'package:flutter_application_1/screens/lawyer_to_client_chat_screen.dart';
import 'package:flutter_application_1/screens/personal_info_screen.dart';

void main() {
  runApp(const ProviderScope(child: LegalTechApp()));
}

/// ✅ ROUTER
final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/auth',
    routes: [
      GoRoute(path: '/auth', builder: (_, _) => const AuthScreen()),
      GoRoute(path: '/client', builder: (_, _) => const ClientDashboard()),
      GoRoute(path: '/lawyer', builder: (_, _) => const LawyerDashboard()),
      GoRoute(path: '/ai-chat', builder: (_, _) => const AIChatScreen()),
      GoRoute(path: '/upload', builder: (_, _) => const UploadScreen()),
      GoRoute(
        path: '/find-lawyers',
        builder: (_, _) => const FindLawyersScreen(),
      ),
      GoRoute(path: '/profile', builder: (_, _) => const ProfileScreen()),
      GoRoute(
        path: '/lawyer-chat',
        builder: (_, _) => const LawyerChatScreen(),
      ),
      GoRoute(
        path: '/lawyer-to-client-chat',
        builder: (_, _) => const LawyerToClientChatScreen(),
      ),
      GoRoute(
        path: '/lawyer/lawyer-profile',
        builder: (_, _) => const LawyerProfileScreen(),
      ),
      GoRoute(
        path: '/edit-profile',
        builder: (context, state) => const EditProfileScreen(),
      ),

      GoRoute(
        path: '/my-clients',
        builder: (context, state) => const MyClientsScreen(),
      ),

      GoRoute(
        path: '/lawyer-availability',
        builder: (context, state) => const LawyerAvailabilityScreen(),
      ),
      GoRoute(
        path: '/personal-info',
        builder: (_, _) => const PersonalInfoScreen(),
      ),
GoRoute(
  path: '/personal-info',
  builder: (_, _) => const PersonalInfoScreen(),
),

GoRoute(path: '/security', builder: (_, _) => const SecurityScreen()),
GoRoute(path: '/payments', builder: (_, _) => const PaymentScreen()),
GoRoute(
  path: '/notifications',
  builder: (_, _) => const NotificationScreen(),
),
GoRoute(path: '/help', builder: (_, _) => const HelpScreen()),
    ],
  );
});

/// ✅ APP
class LegalTechApp extends ConsumerWidget {
  const LegalTechApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final locale = ref.watch(localeProvider);
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp.router(
      title: 'LegalTech Super App',
      debugShowCheckedModeBanner: false,
      routerConfig: router,
      locale: locale,
      themeMode: themeMode,
      theme: _lightTheme(),
      darkTheme: _darkTheme(),

      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      supportedLocales: const [
        Locale('en'),
        Locale('ta'),
        Locale('hi'),
        Locale('ml'),
        Locale('kn'),
        Locale('te'),
      ],
    );
  }

  /// 🌞 LIGHT THEME
  ThemeData _lightTheme() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,

      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        primary: AppColors.primary,
        secondary: AppColors.accent,
        surface: AppColors.surfaceLight,
        background: AppColors.backgroundLight,
        error: AppColors.error,
      ),

      scaffoldBackgroundColor: AppColors.backgroundLight,

      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppColors.textPrimaryLight,
        centerTitle: true,
      ),

      textTheme: GoogleFonts.soraTextTheme(ThemeData.light().textTheme).apply(
        bodyColor: AppColors.textPrimaryLight,
        displayColor: AppColors.textPrimaryLight,
      ),

      cardTheme: CardThemeData(
        color: AppColors.surfaceLight,
        elevation: AppColors.cardElevation,
        shadowColor: AppColors.cardShadow,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFFE2E8F0), width: 2),
        ),
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
          textStyle: GoogleFonts.sora(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.backgroundLight,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 2),
        ),
      ),
    );
  }

  /// 🌙 DARK THEME
  ThemeData _darkTheme() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,

      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.dark,
        primary: AppColors.primaryLight,
        secondary: AppColors.accent,
        surface: AppColors.surfaceDark,
        background: AppColors.backgroundDark,
        error: AppColors.error,
      ),

      scaffoldBackgroundColor: AppColors.backgroundDark,

      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppColors.textPrimaryDark,
        centerTitle: true,
      ),

      textTheme: GoogleFonts.soraTextTheme(ThemeData.dark().textTheme).apply(
        bodyColor: AppColors.textPrimaryDark,
        displayColor: AppColors.textPrimaryDark,
      ),
    );
  }
}
