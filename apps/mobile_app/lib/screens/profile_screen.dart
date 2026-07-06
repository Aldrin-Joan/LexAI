import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:flutter_application_1/providers/theme_provider.dart';
import 'package:google_fonts/google_fonts.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,

      appBar: AppBar(
        title: Text("Profile",
            style: GoogleFonts.sora(fontWeight: FontWeight.w600)),
        centerTitle: true,
      ),

      body: Column(
        children: [
          /// 🔥 Gradient Header (adaptive)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 30, 20, 30),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDark
                    ? [const Color(0xFF1E293B), const Color(0xFF0F172A)]
                    : [const Color(0xFF667EEA), const Color(0xFF764BA2)],
              ),
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(28),
              ),
            ),
            child: Column(
              children: [
                /// Avatar
                Stack(
                  children: [
                    const CircleAvatar(
                      radius: 48,
                      backgroundImage:
                          NetworkImage("https://i.pravatar.cc/300?img=12"),
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.edit, size: 16),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                Text(
                  "Alex Johnson",
                  style: GoogleFonts.sora(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),

                Text(
                  "alex.johnson@example.com",
                  style: GoogleFonts.sora(
                    fontSize: 13,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          /// 🔹 Settings
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
            _item(
  context,
  Icons.person_outline,
  "Personal Information",
  () => context.push('/personal-info'),
),

_item(
  context,
  Icons.lock_outline,
  "Security & Privacy",
  () => context.push('/security'),
),

_item(
  context,
  Icons.payment_outlined,
  "Payment Methods",
  () => context.push('/payments'),
),

_item(
  context,
  Icons.notifications_none,
  "Notifications",
  () => context.push('/notifications'),
),

_item(
  context,
  Icons.help_outline,
  "Help & Support",
  () => context.push('/help'),
),

                const SizedBox(height: 20),

                /// Logout
                Container(
                  margin: const EdgeInsets.only(top: 10),
                  child: ElevatedButton(
                    onPressed: () => context.go('/auth'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.withOpacity(0.1),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      child: Text(
                        "Sign Out",
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
        ],
      ),
    );
  }

  Widget _item(BuildContext context, IconData icon, String title,
      [VoidCallback? onTap]) {
    return ListTile(
      onTap: onTap,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
      tileColor: Theme.of(context).cardColor,
      leading: Icon(icon),
      title: Text(title, style: GoogleFonts.sora(fontSize: 14)),
      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
    );
  }
}