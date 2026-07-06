import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/widgets/chat_bubble.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_application_1/models/chat_message.dart';

// ─────────────────────────────────────────────
//  DESIGN TOKENS
// ─────────────────────────────────────────────
class _DS {
  static const navy      = Color(0xFF0A1628);
  static const blue      = Color(0xFF0B66C2);
  static const blueLight = Color(0xFFE8F1FB);
  static const surface   = Color(0xFFF3F2EE);
  static const divider   = Color(0xFFE0DFDB);
  static const textPrimary   = Color(0xFF141414);
  static const textSecondary = Color(0xFF666666);
  static const textMuted     = Color(0xFF999999);
  static const success   = Color(0xFF057642);

  static const r8    = BorderRadius.all(Radius.circular(8));
  static const r12   = BorderRadius.all(Radius.circular(12));
  static const r20   = BorderRadius.all(Radius.circular(20));
  static const rFull = BorderRadius.all(Radius.circular(100));
}

// ─────────────────────────────────────────────
//  PROVIDER  
// ─────────────────────────────────────────────
class LawyerToClientChatNotifier extends Notifier<List<ChatMessage>> {
  @override
  List<ChatMessage> build() {
    return [
      const ChatMessage(
        content: "Hello, could you review these documents?",
        role: ChatRole.user,
      ),
    ];
  }

  void addMessage(ChatMessage message) {
    state = [...state, message];
  }
}

final lawyerToClientChatProvider =
    NotifierProvider<LawyerToClientChatNotifier, List<ChatMessage>>(
      LawyerToClientChatNotifier.new,
    );

// ─────────────────────────────────────────────
//  SCREEN 
// ─────────────────────────────────────────────
class LawyerToClientChatScreen extends ConsumerStatefulWidget {
  const LawyerToClientChatScreen({super.key});

  @override
  ConsumerState<LawyerToClientChatScreen> createState() =>
      _LawyerToClientChatScreenState();
}

class _LawyerToClientChatScreenState
    extends ConsumerState<LawyerToClientChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isTyping = false;

  void _send() {
    if (_controller.text.trim().isEmpty) return;

    final messageText = _controller.text;
    _controller.clear();
    setState(() => _isTyping = false);

    ref
        .read(lawyerToClientChatProvider.notifier)
        .addMessage(ChatMessage(content: messageText, role: ChatRole.lawyer));

    _scrollToBottom();

    Future.delayed(const Duration(seconds: 2), () {
      if (!mounted) return;
      ref.read(lawyerToClientChatProvider.notifier).addMessage(
            const ChatMessage(
              content: "Sure, let me check that for you.",
              role: ChatRole.user,
            ),
          );
      _scrollToBottom();
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(lawyerToClientChatProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF0F172A) : _DS.surface,

      // ── AppBar ──────────────────────────────
      appBar: AppBar(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: isDark ? const Color(0xFF0F172A) : Colors.white,
        leading: IconButton(
          icon: Icon(
            Icons.arrow_back_rounded,
            color: isDark ? Colors.white : _DS.navy,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        titleSpacing: 0,
        title: Row(
          children: [
            // Avatar with online dot
            Stack(
              clipBehavior: Clip.none,
              children: [
                CircleAvatar(
                  radius: 19,
                  backgroundColor: _DS.navy,
                  child: const Icon(Icons.person,
                      size: 20, color: Colors.white70),
                ),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: _DS.success,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 1.5),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Client Name 1",
                  style: GoogleFonts.dmSans(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: isDark ? Colors.white : _DS.textPrimary,
                  ),
                ),
                Text(
                  "Online",
                  style: GoogleFonts.dmSans(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: _DS.success,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          _appBarAction(
            Icons.call_outlined,
            isDark,
            () {},
          ),
          _appBarAction(
            Icons.videocam_outlined,
            isDark,
            () {},
          ),
          _appBarAction(
            Icons.more_vert_rounded,
            isDark,
            () {},
          ),
          const SizedBox(width: 4),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Divider(
            height: 1,
            color: isDark
                ? Colors.white.withOpacity(0.08)
                : _DS.divider,
          ),
        ),
      ),

      body: Column(
        children: [
          // ── Date chip ──
          _DateChip(label: 'Today', isDark: isDark),

          // ── Messages ──
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(
                  horizontal: 14, vertical: 8),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                final isMe = msg.role == ChatRole.lawyer;

                return Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: _MessageRow(
                    message: msg,
                    isMe: isMe,
                    isDark: isDark,
                    // Passes through to existing ChatBubble widget
                    child: ChatBubble(
                      message: msg,
                      isMeOverride: isMe,
                    ),
                  ),
                );
              },
            ),
          ),

          // ── Input bar ──
          _InputBar(
            controller: _controller,
            isDark: isDark,
            isTyping: _isTyping,
            onChanged: (v) =>
                setState(() => _isTyping = v.trim().isNotEmpty),
            onSend: _send,
          ),
        ],
      ),
    );
  }

  Widget _appBarAction(
      IconData icon, bool isDark, VoidCallback onTap) {
    return IconButton(
      onPressed: onTap,
      icon: Icon(
        icon,
        size: 22,
        color: isDark ? Colors.white70 : _DS.navy,
      ),
    );
  }
}


class _MessageRow extends StatelessWidget {
  final ChatMessage message;
  final bool isMe;
  final bool isDark;
  final Widget child; // ChatBubble

  const _MessageRow({
    required this.message,
    required this.isMe,
    required this.isDark,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final timeStr =
        '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    return Row(
      mainAxisAlignment:
          isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        // Client avatar (left side only)
        if (!isMe) ...[
          CircleAvatar(
            radius: 14,
            backgroundColor: _DS.navy,
            child: const Text(
              'C',
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(width: 6),
        ],

        // ChatBubble + timestamp column
        Column(
          crossAxisAlignment:
              isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            // Your existing ChatBubble 
            child,
            const SizedBox(height: 3),
            // Timestamp + double-tick
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  timeStr,
                  style: GoogleFonts.dmSans(
                    fontSize: 11,
                    color: isDark
                        ? Colors.white38
                        : const Color(0xFF999999),
                  ),
                ),
                if (isMe) ...[
                  const SizedBox(width: 4),
                  Icon(
                    Icons.done_all_rounded,
                    size: 13,
                    color: const Color(0xFF0B66C2),
                  ),
                ],
              ],
            ),
          ],
        ),

        if (isMe) const SizedBox(width: 4),
      ],
    );
  }
}

// ─────────────────────────────────────────────
//  INPUT BAR
// ─────────────────────────────────────────────
class _InputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool isDark;
  final bool isTyping;
  final ValueChanged<String> onChanged;
  final VoidCallback onSend;

  const _InputBar({
    required this.controller,
    required this.isDark,
    required this.isTyping,
    required this.onChanged,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor =
        isDark ? const Color(0xFF0F172A) : Colors.white;
    final fieldColor =
        isDark ? const Color(0xFF1E293B) : const Color(0xFFF3F2EE);
    final hintColor =
        isDark ? Colors.white38 : const Color(0xFF999999);
    final textColor =
        isDark ? Colors.white : const Color(0xFF141414);

    return Container(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 24),
      decoration: BoxDecoration(
        color: bgColor,
        border: Border(
          top: BorderSide(
            color: isDark
                ? Colors.white.withOpacity(0.08)
                : const Color(0xFFE0DFDB),
          ),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // ── Attach ──
          _CircleBtn(
            icon: Icons.attach_file_rounded,
            iconColor: const Color(0xFF666666),
            bg: isDark
                ? const Color(0xFF1E293B)
                : const Color(0xFFF3F2EE),
            onTap: () {},
          ),
          const SizedBox(width: 8),

          // ── Text field ──
          Expanded(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 120),
              decoration: BoxDecoration(
                color: fieldColor,
                borderRadius: _DS.r20,
                border: Border.all(
                  color: isDark
                      ? Colors.white12
                      : const Color(0xFFE0DFDB),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const SizedBox(width: 14),
                  Expanded(
                    child: TextField(
                      controller: controller,
                      maxLines: null,
                      onChanged: onChanged,
                      onSubmitted: (_) => onSend(),
                      style: GoogleFonts.dmSans(
                        fontSize: 14,
                        color: textColor,
                      ),
                      decoration: InputDecoration(
                        hintText: "Type a message…",
                        hintStyle: GoogleFonts.dmSans(
                          fontSize: 13,
                          color: hintColor,
                        ),
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 12),
                      ),
                    ),
                  ),
                  // Mic (hidden when typing)
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 180),
                    child: isTyping
                        ? const SizedBox(width: 12)
                        : Padding(
                            padding: const EdgeInsets.only(
                                right: 10, bottom: 12),
                            child: Icon(
                              Icons.mic_none_rounded,
                              size: 20,
                              color: hintColor,
                            ),
                          ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),

          // ── Send / Like animated swap ──
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 200),
            transitionBuilder: (child, anim) =>
                ScaleTransition(scale: anim, child: child),
            child: isTyping
                ? _CircleBtn(
                    key: const ValueKey('send'),
                    icon: Icons.send_rounded,
                    iconColor: Colors.white,
                    bg: const Color(0xFF0B66C2),
                    onTap: onSend,
                  )
                : _CircleBtn(
                    key: const ValueKey('like'),
                    icon: Icons.thumb_up_outlined,
                    iconColor: const Color(0xFF0B66C2),
                    bg: const Color(0xFFE8F1FB),
                    onTap: () {},
                  ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────
//  SHARED SMALL WIDGETS
// ─────────────────────────────────────────────
class _CircleBtn extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final Color bg;
  final VoidCallback onTap;

  const _CircleBtn({
    super.key,
    required this.icon,
    required this.iconColor,
    required this.bg,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 42,
        height: 42,
        decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
        child: Icon(icon, color: iconColor, size: 20),
      ),
    );
  }
}

class _DateChip extends StatelessWidget {
  final String label;
  final bool isDark;
  const _DateChip({required this.label, required this.isDark});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Center(
        child: Container(
          padding: const EdgeInsets.symmetric(
              horizontal: 14, vertical: 5),
          decoration: BoxDecoration(
            color: isDark
                ? const Color(0xFF1E293B)
                : Colors.white,
            borderRadius: _DS.rFull,
            border: Border.all(
              color: isDark
                  ? Colors.white12
                  : const Color(0xFFE0DFDB),
            ),
          ),
          child: Text(
            label,
            style: GoogleFonts.dmSans(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: isDark
                  ? Colors.white54
                  : const Color(0xFF999999),
            ),
          ),
        ),
      ),
    );
  }
}