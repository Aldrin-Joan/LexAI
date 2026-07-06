import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/models/feed_post.dart';

class FeedController extends Notifier<List<FeedPost>> {
  @override
  List<FeedPost> build() {
    return List.generate(
      5,
      (i) => FeedPost(
        id: i,
        author: 'Adv. Senior Professional ${i + 1}',
        title: 'New Amendment in Patent Law',
        content:
            'I just read the latest Supreme Court judgment on data privacy...',
      ),
    );
  }

  void toggleLike(int id) {
    state = [
      for (final post in state)
        if (post.id == id)
          post.copyWith(
            liked: !post.liked,
            likes: (post.likes + (post.liked ? -1 : 1)).clamp(0, 999),
          )
        else
          post,
    ];
  }

  void toggleFollow(int id) {
    state = [
      for (final post in state)
        post.id == id ? post.copyWith(following: !post.following) : post,
    ];
  }
}

final feedProvider = NotifierProvider<FeedController, List<FeedPost>>(
  FeedController.new,
);
