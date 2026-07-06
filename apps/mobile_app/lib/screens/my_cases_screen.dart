import 'package:flutter/material.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:google_fonts/google_fonts.dart';

class MyCasesScreen extends StatelessWidget {
  const MyCasesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final cases = [
      {
        "title": "Property Dispute",
        "lawyer": "Adv. Sarah Jenkins",
        "date": "2 hours ago",
        "status": "Active",
      },
      {
        "title": "Divorce Case",
        "lawyer": "Adv. Michael Ross",
        "date": "Yesterday",
        "status": "Pending",
      },
      {
        "title": "Contract Review",
        "lawyer": "Adv. Harvey Specter",
        "date": "Oct 24",
        "status": "Completed",
      },
    ];

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,

      appBar: AppBar(
        title: Text(
          "My Cases",
          style: GoogleFonts.sora(
            fontWeight: FontWeight.w600,
            fontSize: 17,
          ),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),

      body: Column(
        children: [
          /// 🔍 SEARCH
          Padding(
            padding: const EdgeInsets.all(16),
            child: Container(
              height: 48,
              padding: const EdgeInsets.symmetric(horizontal: 14),
              decoration: BoxDecoration(
                color: isDark
                    ? AppColors.surfaceDark
                    : AppColors.surfaceLight,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Row(
                children: [
                  const Icon(Icons.search, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      decoration: InputDecoration(
                        hintText: "Search cases...",
                        hintStyle: GoogleFonts.sora(fontSize: 13),
                        border: InputBorder.none,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          /// 📋 CASE LIST
          Expanded(
            child: cases.isEmpty
                ? _emptyState()
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: cases.length,
                    itemBuilder: (context, index) {
                      final item = cases[index];
                      return _caseCard(
                        context,
                        title: item["title"]!,
                        lawyer: item["lawyer"]!,
                        date: item["date"]!,
                        status: item["status"]!,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  /// 📦 CASE CARD
  Widget _caseCard(
    BuildContext context, {
    required String title,
    required String lawyer,
    required String date,
    required String status,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    Color statusColor;
    switch (status) {
      case "Active":
        statusColor = Colors.green;
        break;
      case "Pending":
        statusColor = Colors.orange;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark
            ? AppColors.surfaceDark
            : AppColors.surfaceLight,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDark ? 0.3 : 0.05),
            blurRadius: 12,
          ),
        ],
      ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// TITLE + STATUS
          Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: GoogleFonts.sora(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),

              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  status,
                  style: GoogleFonts.sora(
                    fontSize: 11,
                    color: statusColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          /// LAWYER
          Text(
            lawyer,
            style: GoogleFonts.sora(
              fontSize: 13,
              color: AppColors.textSecondaryLight,
            ),
          ),

          const SizedBox(height: 6),

          /// DATE
          Text(
            date,
            style: GoogleFonts.sora(
              fontSize: 12,
              color: AppColors.textSecondaryLight,
            ),
          ),

          const SizedBox(height: 12),

          /// ACTION BUTTON
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 40,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      "View Details",
                      style: GoogleFonts.sora(
                        color: Colors.white,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Container(
                height: 40,
                width: 40,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.chat_bubble_outline,
                  size: 18,
                  color: AppColors.primary,
                ),
              ),
            ],
          )
        ],
      ),
    );
  }

  /// 😴 EMPTY STATE
  Widget _emptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.folder_open, size: 50),
          const SizedBox(height: 12),
          Text(
            "No cases yet",
            style: GoogleFonts.sora(fontSize: 16),
          ),
        ],
      ),
    );
  }
}