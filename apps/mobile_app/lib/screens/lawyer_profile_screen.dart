import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:go_router/go_router.dart';

class LawyerProfileScreen extends StatelessWidget {
  const LawyerProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,

      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            /// 👤 PROFILE HEADER
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: LinearGradient(
                  colors: isDark
                      ? const [Color(0xFF1E293B), Color(0xFF0F172A)]
                      : const [Color(0xFF667EEA), Color(0xFF764BA2)],
                ),
              ),
              child: Column(
                children: [
                  const CircleAvatar(
                    radius: 40,
                    backgroundColor: Colors.white,
                    child: Icon(Icons.person, size: 40),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    "Adv. John Doe",
                    style: GoogleFonts.sora(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Corporate Lawyer",
                    style: GoogleFonts.sora(
                      color: Colors.white70,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _stat("120", "Cases"),
                      _stat("4.8", "Rating"),
                      _stat("5 yrs", "Experience"),
                    ],
                  )
                ],
              ),
            ),

            const SizedBox(height: 24),

            /// OPTIONS
            _tile(context, "Edit Profile", Icons.edit_outlined),
            _tile(context, "My Clients", Icons.people_outline),
            _tile(context, "Earnings", Icons.currency_rupee),
            _tile(context, "Settings", Icons.settings_outlined),

            const SizedBox(height: 24),

            /// 🚪 LOGOUT (FIXED ONLY THIS)
            GestureDetector(
              onTap: () {
                final parentContext = context; // ✅ IMPORTANT

                showDialog(
                  context: context,
                  builder: (dialogContext) => AlertDialog(
                    title: const Text("Logout"),
                    content:
                        const Text("Are you sure you want to logout?"),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(dialogContext),
                        child: const Text("Cancel"),
                      ),
                      FilledButton(
                        onPressed: () {
                          Navigator.pop(dialogContext);

                          // 🔥 FIX: use parentContext
                          Future.delayed(Duration.zero, () {
                            parentContext.go('/auth');
                          });
                        },
                        child: const Text("Logout"),
                      ),
                    ],
                  ),
                );
              },
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Center(
                  child: Text(
                    "Logout",
                    style: GoogleFonts.sora(
                      color: Colors.red,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 📊 STATS
  Widget _stat(String value, String label) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.sora(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.sora(
            color: Colors.white70,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  /// ⚙️ TILE
  Widget _tile(BuildContext context, String title, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppColors.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: GoogleFonts.sora(fontSize: 14),
            ),
          ),
          const Icon(Icons.arrow_forward_ios, size: 16),
        ],
      ),
    );
  }
}