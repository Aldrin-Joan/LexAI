import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_application_1/theme/app_colors.dart';

class SecurityScreen extends StatelessWidget {
  const SecurityScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(title: const Text("Security & Privacy")),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _tile("Change Password", Icons.lock_outline),
          _tile("Two-Factor Authentication", Icons.verified_user_outlined),
          _tile("Privacy Settings", Icons.security_outlined),
        ],
      ),
    );
  }

  Widget _tile(String title, IconData icon) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(vertical: 8),
      leading: Icon(icon, color: AppColors.primary),
      title: Text(title, style: GoogleFonts.sora()),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () {},
    );
  }
}