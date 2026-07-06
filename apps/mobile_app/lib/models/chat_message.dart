enum ChatRole { user, ai, lawyer }

class ChatMessage {
  final ChatRole role;
  final String content;
  final String? audioUrl;       // URL to the MP3 audio response (voice queries only)
  final String? transcription;  // Original language transcription (voice queries only)
  final bool isLoading;         // True while waiting for backend response

  const ChatMessage({
    required this.role,
    required this.content,
    this.audioUrl,
    this.transcription,
    this.isLoading = false,
  });
}
