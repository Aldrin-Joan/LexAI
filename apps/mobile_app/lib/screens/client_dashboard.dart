import 'dart:ui'; 
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/l10n/app_localizations.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:flutter_application_1/providers/client_nav_provider.dart';
import 'package:flutter_application_1/widgets/dashboard_widgets.dart';
import 'package:flutter_application_1/screens/ai_chat_screen.dart';
import 'package:flutter_application_1/screens/profile_screen.dart';
import 'package:flutter_application_1/screens/my_cases_screen.dart';

class ClientDashboard extends ConsumerWidget {
  const ClientDashboard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final navIndex = ref.watch(clientNavIndexProvider);

    return Scaffold(
      body: SafeArea(
        child: _buildScreen(navIndex, context, ref),
      ),
      bottomNavigationBar: _bottomNav(ref, navIndex), // ✅ updated UI
    );
  }

  Widget _buildScreen(int index, BuildContext context, WidgetRef ref) {
    switch (index) {
      case 1:
        return const AIChatScreen();
      case 2:
        return const ProfileScreen();
      case 3:
        return const MyCasesScreen();
      default:
        return _homeScreen(context, ref);
    }
  }

  Widget _homeScreen(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 24),

          Text(
            "Good Morning,",
            style: GoogleFonts.sora(
              fontSize: 16,
              color: theme.colorScheme.onBackground.withOpacity(0.6),
            ),
          ),

          const SizedBox(height: 16),

          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 18,
            mainAxisSpacing: 18,
            childAspectRatio: 0.95,
            children: [
              ActionCard(
                title: l10n.aiChat,
                subtitle: "Ask legal questions",
                icon: Icons.auto_awesome_rounded,
                color: ActionCardColor.purple,
                onTap: () {
                  ref.read(clientNavIndexProvider.notifier).setIndex(1);
                },
              ),
              ActionCard(
                title: l10n.uploadDocs,
                subtitle: "Review contracts",
                icon: Icons.upload_file_rounded,
                color: ActionCardColor.green,
                onTap: () => context.push('/upload'),
              ),
              ActionCard(
                title: l10n.findLawyers,
                subtitle: "Expert consultation",
                icon: Icons.gavel_rounded,
                color: ActionCardColor.amber,
                onTap: () => context.push('/find-lawyers'),
              ),
              ActionCard(
                title: "My Cases",
                subtitle: "Track progress",
                icon: Icons.folder_open_rounded,
                color: ActionCardColor.purple,
                onTap: () {
                  ref.read(clientNavIndexProvider.notifier).setIndex(3);
                },
              ),
            ],
          ),

          const SizedBox(height: 24),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.recentConsultations,
                style: GoogleFonts.sora(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                "See all",
                style: GoogleFonts.sora(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: 3,
            separatorBuilder: (_, __) => const SizedBox(height: 14),
            itemBuilder: (context, index) {
              final titles = [
                "Property Dispute",
                "Contract Review",
                "Family Law Inquiry",
              ];
              final dates = ["2 hours ago", "Yesterday", "Oct 24"];
              final statuses = [
                "In Progress",
                "Completed",
                "Pending"
              ];

              return ConsultationItem(
                title: titles[index],
                date: dates[index],
                status: statuses[index],
                onTap: () {},
              );
            },
          ),

          const SizedBox(height: 80),
        ],
      ),
    );
  }

  /// 🌊 UPDATED PREMIUM BOTTOM NAV
  Widget _bottomNav(WidgetRef ref, int navIndex) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.85),
              borderRadius: BorderRadius.circular(28),
              border: Border.all(color: Colors.white.withOpacity(0.2)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.12),
                  blurRadius: 25,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _NavItem(
                  icon: Icons.dashboard_rounded,
                  label: "Home",
                  isActive: navIndex == 0,
                  onTap: () =>
                      ref.read(clientNavIndexProvider.notifier).setIndex(0),
                ),
                _NavItem(
                  icon: Icons.chat_bubble_rounded,
                  label: "Chat",
                  isActive: navIndex == 1,
                  onTap: () =>
                      ref.read(clientNavIndexProvider.notifier).setIndex(1),
                ),
                _NavItem(
                  icon: Icons.folder_open_rounded,
                  label: "Cases",
                  isActive: navIndex == 3,
                  onTap: () =>
                      ref.read(clientNavIndexProvider.notifier).setIndex(3),
                ),
                _NavItem(
                  icon: Icons.person_rounded,
                  label: "Profile",
                  isActive: navIndex == 2,
                  onTap: () =>
                      ref.read(clientNavIndexProvider.notifier).setIndex(2),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// 🔹 UPDATED NAV ITEM (visibility fixed)
class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isActive
              ? AppColors.primary.withOpacity(0.15)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 24,
              color: isActive
                  ? AppColors.primary
                  : Colors.grey.shade600, // ✅ fixed
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: GoogleFonts.sora(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: isActive
                    ? AppColors.primary
                    : Colors.grey.shade600, // ✅ fixed
              ),
            ),
          ],
        ),
      ),
    );
  }
}