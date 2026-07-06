import 'package:flutter/material.dart';

/// Centralized color tokens for the app.
/// Works with Material 3 + light/dark themes.
abstract final class AppColors {
  // ===== Brand =====
  static const Color primary = Color(0xFF1E3A8A); // Deep Blue
  static const Color primaryLight = Color(0xFF3B82F6); // Light Blue
  static const Color primaryDark = Color(0xFF1E293B); // Dark Slate

  static const Color accent = Color(0xFF10B981); // Emerald Green
  static const Color accentTeal = Color(0xFF14B8A6); // Teal

  static const Color warm = Color(0xFFF59E0B); // Amber Warning

  // ===== Neutral / Surfaces =====
  static const Color backgroundLight = Color(0xFFF8FAFC); // Slate 50
  static const Color backgroundDark = Color(0xFF0F172A); // Slate 900

  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color surfaceDark = Color(0xFF1E293B); // Slate 800

  // ===== Text =====
  static const Color textPrimaryLight = Color(0xFF0F172A); // Slate 900
  static const Color textPrimaryDark = Color(0xFFF8FAFC); // Slate 50

  static const Color textSecondaryLight = Color(0xFF64748B); // Slate 500
  static const Color textSecondaryDark = Color(0xFF94A3B8); // Slate 400

  // ===== Status =====
  static const Color success = Color(0xFF10B981);
  static const Color error = Color(0xFFEF4444);
  static const Color warning = Color(0xFFF59E0B);
  static const Color info = Color(0xFF3B82F6);

  // ===== Effects =====
  static const Color cardShadow = Color.fromRGBO(0, 0, 0, 0.1);
  static const double cardElevation = 4.0;
}
