import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen> {
  bool push = true;
  bool email = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Notifications")),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          SwitchListTile(
            title: Text("Push Notifications", style: GoogleFonts.sora()),
            value: push,
            onChanged: (v) => setState(() => push = v),
          ),
          SwitchListTile(
            title: Text("Email Notifications", style: GoogleFonts.sora()),
            value: email,
            onChanged: (v) => setState(() => email = v),
          ),
        ],
      ),
    );
  }
}