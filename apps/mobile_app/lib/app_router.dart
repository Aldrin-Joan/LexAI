import 'package:go_router/go_router.dart';

import 'screens/auth_screen.dart';
import 'screens/client_dashboard.dart';
import 'screens/lawyer_dashboard.dart';
import 'screens/ai_chat_screen.dart';
import 'screens/upload_screen.dart';
import 'screens/find_lawyers_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/lawyer_chat_screen.dart';
import 'screens/lawyer_to_client_chat_screen.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/auth',
  routes: [
    GoRoute(
      path: '/auth',
      builder: (context, state) => const AuthScreen(),
    ),
    GoRoute(
      path: '/client',
      builder: (context, state) => const ClientDashboard(),
    ),
    GoRoute(
      path: '/lawyer',
      builder: (context, state) => const LawyerDashboard(),
    ),
    GoRoute(
      path: '/ai-chat',
      builder: (context, state) => const AIChatScreen(),
    ),
    GoRoute(
      path: '/upload',
      builder: (context, state) => const UploadScreen(),
    ),
    GoRoute(
      path: '/find-lawyers',
      builder: (context, state) => const FindLawyersScreen(),
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/lawyer-chat',
      builder: (context, state) => const LawyerChatScreen(),
    ),
    GoRoute(
      path: '/lawyer-to-client-chat',
      builder: (context, state) => const LawyerToClientChatScreen(),
    ),
  ],
);