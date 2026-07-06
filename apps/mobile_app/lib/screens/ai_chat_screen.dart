import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/providers/chat_controller.dart';
import 'package:flutter_application_1/models/chat_message.dart';
import 'package:google_fonts/google_fonts.dart';

class AIChatScreen extends ConsumerStatefulWidget {
  const AIChatScreen({super.key});

  @override
  ConsumerState<AIChatScreen> createState() => _AIChatScreenState();
}

class _AIChatScreenState extends ConsumerState<AIChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scroll = ScrollController();

  void _send() {
    if (_controller.text.trim().isEmpty) return;
    ref.read(chatProvider.notifier).sendTextMessage(_controller.text);
    _controller.clear();

    Future.delayed(const Duration(milliseconds: 200), () {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0B0C0F),

      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        centerTitle: true,
        title: Text(
          "Lawgix",
          style: GoogleFonts.sora(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),

      body: Column(
        children: [
          /// Messages OR hero
          Expanded(
            child: messages.isEmpty
                ? _hero()
                : ListView.builder(
                    controller: _scroll,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 20,
                    ),
                    itemCount: messages.length,
                    itemBuilder: (context, i) {
                      final msg = messages[i];
                      return _bubble(msg.content, msg.role == ChatRole.user);
                    },
                  ),
          ),

          /// bottom input only when chat started
          if (messages.isNotEmpty) _inputBar(),
        ],
      ),
    );
  }

  /// ⭐ HERO (Gemini style)
  Widget _hero() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.auto_awesome, size: 48, color: Color(0xFF7C9BFF)),
            const SizedBox(height: 20),

            Text(
              "Meet Lawgix,\nyour legal AI assistant",
              textAlign: TextAlign.center,
              style: GoogleFonts.sora(
                fontSize: 28,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),

            const SizedBox(height: 30),

            _heroInput(),

            const SizedBox(height: 20),

            _suggestionPills(),
          ],
        ),
      ),
    );
  }

  /// ⭐ Large hero input
  Widget _heroInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1F24),
        borderRadius: BorderRadius.circular(28),
      ),
      child: Row(
        children: [
          const Icon(Icons.add, color: Colors.grey),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _controller,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                hintText: "Ask Lawgix…",
                hintStyle: TextStyle(color: Colors.grey),
                border: InputBorder.none,
              ),
              onSubmitted: (_) => _send(),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send, color: Colors.grey),
            onPressed: _send,
          ),
        ],
      ),
    );
  }

  /// ⭐ Suggestion pills
  Widget _suggestionPills() {
    final items = [
      "Contract review",
      "Property dispute",
      "Divorce process",
      "Startup legal",
    ];

    return Wrap(
      spacing: 10,
      children: items.map((e) {
        return GestureDetector(
          onTap: () {
            _controller.text = e;
            _send();
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF1E1F24),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(e, style: const TextStyle(color: Colors.white70)),
          ),
        );
      }).toList(),
    );
  }

  /// ⭐ Bubble
  Widget _bubble(String text, bool isUser) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.all(14),
        constraints: const BoxConstraints(maxWidth: 420),
        decoration: BoxDecoration(
          color: isUser ? const Color(0xFF5B7FFF) : const Color(0xFF1E1F24),
          borderRadius: BorderRadius.circular(24),
        ),
        child: Text(text, style: GoogleFonts.sora(color: Colors.white)),
      ),
    );
  }

  /// ⭐ Bottom input after chat starts
  Widget _inputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1F24),
          borderRadius: BorderRadius.circular(30),
        ),
        child: Row(
          children: [
            const Icon(Icons.mic_none, color: Colors.grey),
            const SizedBox(width: 8),
            Expanded(
              child: TextField(
                controller: _controller,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: "Ask Lawgix…",
                  hintStyle: TextStyle(color: Colors.grey),
                  border: InputBorder.none,
                ),
                onSubmitted: (_) => _send(),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.send, color: Colors.white),
              onPressed: _send,
            ),
          ],
        ),
      ),
    );
  }
}
