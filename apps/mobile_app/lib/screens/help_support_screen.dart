import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Help & Support")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("FAQs", style: GoogleFonts.sora(fontSize: 16, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            Text("• How to upload documents?\n• How to contact lawyer?",
                style: GoogleFonts.sora()),

            const SizedBox(height: 24),

            Text("Contact Support", style: GoogleFonts.sora(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),

            Text("support@lawgix.com", style: GoogleFonts.sora()),
          ],
        ),
      ),
    );
  }
}