import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/widgets/chat_bubble.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_application_1/models/chat_message.dart';

/// ✅ NOTIFIER
class LawyerChatNotifier extends Notifier<List<ChatMessage>> {
  @override
  List<ChatMessage> build() {
    return [
      const ChatMessage(
        content: "Hello, how can I help you with your property query?",
        role: ChatRole.lawyer,
      ),
    ];
  }

  void addMessage(ChatMessage message) {
    state = [...state, message];
  }
}

/// ✅ PROVIDER
final lawyerChatProvider =
    NotifierProvider<LawyerChatNotifier, List<ChatMessage>>(
  LawyerChatNotifier.new,
);

/// ✅ SCREEN
class LawyerChatScreen extends ConsumerStatefulWidget {
  const LawyerChatScreen({super.key});

  @override
  ConsumerState<LawyerChatScreen> createState() =>
      _LawyerChatScreenState();
}

class _LawyerChatScreenState
    extends ConsumerState<LawyerChatScreen> {
  final TextEditingController _controller = TextEditingController();

  void _send() {
    if (_controller.text.trim().isEmpty) return;

    final text = _controller.text;
    _controller.clear();

    ref.read(lawyerChatProvider.notifier).addMessage(
          ChatMessage(content: text, role: ChatRole.user),
        );

    Future.delayed(const Duration(seconds: 1), () {
      if (!mounted) return;

      ref.read(lawyerChatProvider.notifier).addMessage(
            const ChatMessage(
              content:
                  "I understand. Can you share more details about your case?",
              role: ChatRole.lawyer,
            ),
          );
    });
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(lawyerChatProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,

      /// 🔥 APPBAR
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        centerTitle: true,
        title: Column(
          children: [
            Text(
              "Lawgix AI",
              style: GoogleFonts.sora(
                fontSize: 17,
                fontWeight: FontWeight.w600,
                color: isDark
                    ? Colors.white
                    : AppColors.textPrimaryLight,
              ),
            ),
            Text(
              "Legal Assistant",
              style: GoogleFonts.sora(
                fontSize: 12,
                color: AppColors.textSecondaryLight,
              ),
            ),
          ],
        ),
      ),

      body: Column(
        children: [
          /// 💬 CHAT AREA
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).scaffoldBackgroundColor,
                    AppColors.primary.withOpacity(0.05),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 16,
                ),
                itemCount: messages.length,
                itemBuilder: (context, index) {
                  final msg = messages[index];
                  final isUser = msg.role == ChatRole.user;

                  return Align(
                    alignment: isUser
                        ? Alignment.centerRight
                        : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(14),
                      constraints:
                          const BoxConstraints(maxWidth: 280),
                      decoration: BoxDecoration(
                        color: isUser
                            ? AppColors.primary
                            : (isDark
                                ? const Color(0xFF1E293B)
                                : Colors.white),
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: isUser
                                ? AppColors.primary.withOpacity(0.3)
                                : Colors.black.withOpacity(0.08),
                            blurRadius: 10,
                          ),
                        ],
                      ),
                      child: Text(
                        msg.content,
                        style: GoogleFonts.sora(
                          fontSize: 15,
                          height: 1.4,
                          color: isUser
                              ? Colors.white
                              : (isDark
                                  ? Colors.white
                                  : AppColors.textPrimaryLight),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ),

          /// ✨ INPUT BAR
          Container(
            padding:
                const EdgeInsets.fromLTRB(16, 10, 16, 16),
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 14),
              decoration: BoxDecoration(
                color: isDark
                    ? const Color(0xFF0F172A)
                    : Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(28),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 12,
                  )
                ],
              ),
              child: Row(
                children: [
                  const Icon(Icons.add, size: 20),

                  const SizedBox(width: 8),

                  Expanded(
                    child: TextField(
                      controller: _controller,
                      style: GoogleFonts.sora(
                        fontSize: 15,
                        color: isDark
                            ? Colors.white
                            : AppColors.textPrimaryLight,
                      ),
                      decoration: InputDecoration(
                        hintText: "Ask Lawgix anything...",
                        hintStyle: GoogleFonts.sora(
                          fontSize: 14,
                          color: Colors.grey.shade500,
                        ),
                        border: InputBorder.none,
                      ),
                      onSubmitted: (_) => _send(),
                    ),
                  ),

                  const Icon(Icons.mic_none, size: 20),

                  const SizedBox(width: 8),

                  GestureDetector(
                    onTap: _send,
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.send,
                        size: 16,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}