import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class LawyerAvailabilityScreen extends StatefulWidget {
  const LawyerAvailabilityScreen({super.key});

  @override
  State<LawyerAvailabilityScreen> createState() =>
      _LawyerAvailabilityScreenState();
}

class _LawyerAvailabilityScreenState extends State<LawyerAvailabilityScreen> {
  bool isAvailable = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF3F2EF),
      appBar: AppBar(
        title: const Text("Availability"),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            SwitchListTile(
              value: isAvailable,
              onChanged: (val) {
                setState(() => isAvailable = val);
              },
              title: Text(
                "Available for Consultation",
                style: GoogleFonts.sora(fontWeight: FontWeight.w600),
              ),
            ),

            const SizedBox(height: 20),

            TextField(
              decoration: InputDecoration(
                labelText: "Available Time Slot",
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),

            const SizedBox(height: 20),

            ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0A66C2),
              ),
              child: const Text("Update"),
            ),
          ],
        ),
      ),
    );
  }
}
