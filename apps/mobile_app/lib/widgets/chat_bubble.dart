import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_application_1/models/chat_message.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:google_fonts/google_fonts.dart';

class ChatBubble extends StatefulWidget {
  final ChatMessage message;
  final bool? isMeOverride;

  const ChatBubble({super.key, required this.message, this.isMeOverride});

  @override
  State<ChatBubble> createState() => _ChatBubbleState();
}

class _ChatBubbleState extends State<ChatBubble> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isPlaying = false;

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _toggleAudio(String url) async {
    if (_isPlaying) {
      await _audioPlayer.stop();
      setState(() => _isPlaying = false);
    } else {
      setState(() => _isPlaying = true);
      await _audioPlayer.play(UrlSource(url));
      _audioPlayer.onPlayerComplete.listen((_) {
        if (mounted) setState(() => _isPlaying = false);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final message = widget.message;
    final isUserRole = message.role == ChatRole.user;
    final isLawyerScale = message.role == ChatRole.lawyer;
    final isAI = message.role == ChatRole.ai;
    final isMe = widget.isMeOverride ?? isUserRole;
    final isReceived = !isMe;
    final bool showHeader = isReceived && (isAI || isLawyerScale);

    Color? getBackgroundColor() {
      if (isMe) return AppColors.surfaceLight;
      if (isAI) return null;
      if (isLawyerScale) return null;
      return Colors.white;
    }

    Gradient? getGradient() {
      if (isMe) return null;
      if (isAI) {
        return const LinearGradient(
          colors: [Color(0xFFEEF2FF), Color(0xFFE0E7FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      }
      if (isLawyerScale) {
        return const LinearGradient(
          colors: [Color(0xFFF0FDF4), Color(0xFFDCFCE7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      }
      return null;
    }

    Color getBorderColor() {
      if (isMe) return const Color(0xFFE2E8F0);
      if (isAI) return const Color(0xFFC7D2FE);
      if (isLawyerScale) return const Color(0xFFBBF7D0);
      return const Color(0xFFE2E8F0);
    }

    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
        ),
        decoration: BoxDecoration(
          color: getBackgroundColor(),
          gradient: getGradient(),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(20),
            topRight: const Radius.circular(20),
            bottomLeft: isMe ? const Radius.circular(20) : Radius.zero,
            bottomRight: isMe ? Radius.zero : const Radius.circular(20),
          ),
          border: Border.all(color: getBorderColor(), width: 1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 2,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Header (AI / Lawyer label) ────────────────────────────────────
            if (showHeader) ...[
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      isAI ? Icons.smart_toy_rounded : Icons.gavel_rounded,
                      size: 14,
                      color: isAI ? AppColors.primary : AppColors.accent,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    isAI ? 'Legal AI' : 'Adv. Sarah Jenkins',
                    style: GoogleFonts.sora(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isAI ? AppColors.primary : AppColors.accent,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
            ],

            // ── Loading spinner ───────────────────────────────────────────────
            if (message.isLoading)
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: isAI ? AppColors.primary : AppColors.textSecondaryLight,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    isAI ? 'Thinking...' : 'Processing audio...',
                    style: GoogleFonts.sora(
                      fontSize: 14,
                      color: AppColors.textSecondaryLight,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              )
            else ...[
              // ── Message content ─────────────────────────────────────────────
              Text(
                message.content,
                style: GoogleFonts.sora(
                  fontSize: 15,
                  height: 1.5,
                  color: AppColors.textPrimaryLight,
                  fontWeight: FontWeight.w400,
                ),
              ),

              // ── Audio playback button (voice responses only) ────────────────
              if (message.audioUrl != null) ...[
                const SizedBox(height: 12),
                GestureDetector(
                  onTap: () => _toggleAudio(message.audioUrl!),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: AppColors.primary.withOpacity(0.4),
                        width: 1.5,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.1),
                          blurRadius: 6,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _isPlaying
                              ? Icons.stop_circle_rounded
                              : Icons.play_circle_rounded,
                          color: AppColors.primary,
                          size: 20,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          _isPlaying ? 'Stop Audio' : '▶ Play Audio Response',
                          style: GoogleFonts.sora(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: AppColors.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}
