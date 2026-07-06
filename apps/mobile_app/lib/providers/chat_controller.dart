import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/models/chat_message.dart';
import 'package:flutter_application_1/services/voice_api_service.dart';

class ChatController extends Notifier<List<ChatMessage>> {
  @override
  List<ChatMessage> build() => const [
        ChatMessage(
          role: ChatRole.ai,
          content:
              'Namaste! 🙏 I am your AI Legal Assistant. You can type your question or tap the mic to speak in Hindi, Tamil, or any Indian language.',
        ),
      ];

  // ── Text Query ─────────────────────────────────────────────────────────────

  Future<void> sendTextMessage(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return;

    // 1. Add user bubble + loading AI bubble
    state = [
      ...state,
      ChatMessage(role: ChatRole.user, content: trimmed),
      const ChatMessage(role: ChatRole.ai, content: '', isLoading: true),
    ];

    try {
      final result = await VoiceApiService.sendTextQuery(trimmed);
      final answer = result['response'] as String? ?? 'No response received.';

      _replaceLastLoadingWith(ChatMessage(role: ChatRole.ai, content: answer));
    } catch (e) {
      _replaceLastLoadingWith(
        ChatMessage(
          role: ChatRole.ai,
          content: '⚠️ Error connecting to server. Please make sure the backend is running.\n\nDetails: $e',
        ),
      );
    }
  }

  // ── Voice Query ────────────────────────────────────────────────────────────

  Future<void> sendVoiceMessage(File audioFile) async {
    // 1. Add user bubble (will show transcription once received)
    state = [
      ...state,
      const ChatMessage(role: ChatRole.user, content: '🎤 Processing your voice...', isLoading: true),
      const ChatMessage(role: ChatRole.ai, content: '', isLoading: true),
    ];

    try {
      final result = await VoiceApiService.sendVoiceQuery(audioFile);

      final transcription = result['transcription'] as String? ?? '';
      final answerText = result['answer_text'] as String? ?? 'No response received.';
      final relativeAudioUrl = result['audio_url'] as String?;
      final fullAudioUrl = relativeAudioUrl != null
          ? VoiceApiService.buildAudioUrl(relativeAudioUrl)
          : null;

      // Replace the user loading bubble with transcription
      final messages = List<ChatMessage>.from(state);
      // Find the two loading bubbles (last two)
      final lastUserIdx = messages.lastIndexWhere(
        (m) => m.role == ChatRole.user && m.isLoading,
      );
      final lastAiIdx = messages.lastIndexWhere(
        (m) => m.role == ChatRole.ai && m.isLoading,
      );

      if (lastUserIdx != -1) {
        messages[lastUserIdx] = ChatMessage(
          role: ChatRole.user,
          content: transcription.isNotEmpty
              ? '🎤 "$transcription"'
              : '🎤 Voice message sent',
        );
      }
      if (lastAiIdx != -1) {
        messages[lastAiIdx] = ChatMessage(
          role: ChatRole.ai,
          content: answerText,
          audioUrl: fullAudioUrl,
          transcription: transcription,
        );
      }
      state = messages;
    } catch (e) {
      // Replace both loading bubbles with error messages
      final messages = List<ChatMessage>.from(state);
      final lastUserIdx = messages.lastIndexWhere(
        (m) => m.role == ChatRole.user && m.isLoading,
      );
      final lastAiIdx = messages.lastIndexWhere(
        (m) => m.role == ChatRole.ai && m.isLoading,
      );
      if (lastUserIdx != -1) {
        messages[lastUserIdx] = const ChatMessage(
          role: ChatRole.user,
          content: '🎤 Voice message (failed)',
        );
      }
      if (lastAiIdx != -1) {
        messages[lastAiIdx] = ChatMessage(
          role: ChatRole.ai,
          content: '⚠️ Could not process voice query. Please make sure the backend is running.\n\nDetails: $e',
        );
      }
      state = messages;
    }
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  void _replaceLastLoadingWith(ChatMessage replacement) {
    final messages = List<ChatMessage>.from(state);
    final idx = messages.lastIndexWhere((m) => m.isLoading);
    if (idx != -1) messages[idx] = replacement;
    state = messages;
  }
}

final chatProvider = NotifierProvider<ChatController, List<ChatMessage>>(
  ChatController.new,
);

