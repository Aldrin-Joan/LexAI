enum FeedAction { like, follow }

class FeedPost {
  final int id;
  final String author;
  final String title;
  final String content;
  final int likes;
  final bool liked;
  final bool following;

  const FeedPost({
    required this.id,
    required this.author,
    required this.title,
    required this.content,
    this.likes = 0,
    this.liked = false,
    this.following = false,
  });

  FeedPost copyWith({int? likes, bool? liked, bool? following}) {
    return FeedPost(
      id: id,
      author: author,
      title: title,
      content: content,
      likes: likes ?? this.likes,
      liked: liked ?? this.liked,
      following: following ?? this.following,
    );
  }
}
