import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/l10n/app_localizations.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_application_1/models/feed_post.dart';
import 'package:flutter_application_1/providers/feed_controller.dart';
import 'package:flutter_application_1/theme/app_colors.dart';
import 'package:google_fonts/google_fonts.dart';

// ─────────────────────────────────────────────
//  DESIGN SYSTEM
// ─────────────────────────────────────────────
class _DS {
  static const navy      = Color(0xFF0A1628);
  static const blue      = Color(0xFF0B66C2);
  static const blueLight = Color(0xFFE8F1FB);
  static const surface   = Color(0xFFF3F2EE);
  static const card      = Colors.white;
  static const divider   = Color(0xFFE0DFDB);
  static const textPrimary   = Color(0xFF141414);
  static const textSecondary = Color(0xFF666666);
  static const textMuted     = Color(0xFF999999);
  static const success   = Color(0xFF057642);
  static const gold      = Color(0xFFF5A623);

  static const r8    = BorderRadius.all(Radius.circular(8));
  static const r12   = BorderRadius.all(Radius.circular(12));
  static const r20   = BorderRadius.all(Radius.circular(20));
  static const rFull = BorderRadius.all(Radius.circular(100));

  static List<BoxShadow> cardShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.06),
      blurRadius: 6,
      offset: const Offset(0, 2),
    ),
  ];
}

class _T {
  static TextStyle get h1 => GoogleFonts.dmSans(
      fontSize: 20, fontWeight: FontWeight.w700, color: _DS.textPrimary);
  static TextStyle get h2 => GoogleFonts.dmSans(
      fontSize: 16, fontWeight: FontWeight.w600, color: _DS.textPrimary);
  static TextStyle get h3 => GoogleFonts.dmSans(
      fontSize: 14, fontWeight: FontWeight.w600, color: _DS.textPrimary);
  static TextStyle get body => GoogleFonts.dmSans(
      fontSize: 14, fontWeight: FontWeight.w400, color: _DS.textPrimary);
  static TextStyle get bodySmall => GoogleFonts.dmSans(
      fontSize: 13, fontWeight: FontWeight.w400, color: _DS.textSecondary);
  static TextStyle get caption => GoogleFonts.dmSans(
      fontSize: 12, fontWeight: FontWeight.w400, color: _DS.textMuted);
  static TextStyle get label => GoogleFonts.dmSans(
      fontSize: 12, fontWeight: FontWeight.w600, color: _DS.textSecondary);
}

// ─────────────────────────────────────────────
//  PROFILE — UNCHANGED (exactly as provided)
// ─────────────────────────────────────────────
class LawyerProfileView extends StatelessWidget {
  const LawyerProfileView({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // ── Profile hero card ──
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.all(Radius.circular(12)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                const CircleAvatar(
                  radius: 40,
                  backgroundColor: Color(0xFF0A1628),
                  child: Icon(Icons.person, size: 40, color: Colors.white70),
                ),
                const SizedBox(height: 12),
                Text(
                  "Adv. Lawyer",
                  style: GoogleFonts.sora(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF141414),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  "Senior Advocate",
                  style: GoogleFonts.sora(
                    fontSize: 13,
                    color: const Color(0xFF666666),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Menu tiles card ──
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.all(Radius.circular(12)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                _tile(context, "Edit Profile",      Icons.edit_outlined),
                Divider(height: 1, indent: 56, color: const Color(0xFFE0DFDB)),
                _tile(context, "My Clients",        Icons.people_outline_rounded),
                Divider(height: 1, indent: 56, color: const Color(0xFFE0DFDB)),
                _tile(context, "Set Availability",  Icons.calendar_today_outlined),
                Divider(height: 1, indent: 56, color: const Color(0xFFE0DFDB)),
                _tile(context, "Settings",          Icons.settings_outlined),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ── Logout ──
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              icon: const Icon(Icons.logout_rounded,
                  color: Colors.redAccent, size: 18),
              label: Text(
                "Logout",
                style: GoogleFonts.sora(
                  color: Colors.redAccent,
                  fontWeight: FontWeight.w600,
                ),
              ),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.redAccent),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(12)),
                ),
              ),
              onPressed: () => context.go('/auth'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _tile(BuildContext context, String title, IconData icon) {
    return ListTile(
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: const Color(0xFFE8F1FB),
          borderRadius: const BorderRadius.all(Radius.circular(8)),
        ),
        child: Icon(icon, size: 18, color: const Color(0xFF0B66C2)),
      ),
      title: Text(
        title,
        style: GoogleFonts.sora(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: const Color(0xFF141414),
        ),
      ),
      trailing: const Icon(
        Icons.arrow_forward_ios,
        size: 14,
        color: Color(0xFF999999),
      ),
      onTap: () {
        if (title == "Edit Profile") {
          context.push('/edit-profile');
        } else if (title == "My Clients") {
          context.push('/my-clients');
        } else if (title == "Set Availability") {
          context.push('/lawyer-availability');
        }
      },
    );
  }
}

// ─────────────────────────────────────────────
//  AI TOOLS VIEW
// ─────────────────────────────────────────────
class AIToolsView extends StatelessWidget {
  const AIToolsView({super.key});

  static const _tools = [
    (Icons.description_outlined,   'Draft Contract',   'Generate legal contracts instantly',       Color(0xFF0B66C2)),
    (Icons.search_outlined,         'Case Research',    'Find precedents and citations',            Color(0xFF057642)),
    (Icons.summarize_outlined,      'Summarize Doc',    'Get key points from any document',         Color(0xFF7C3AED)),
    (Icons.gavel_outlined,          'Argue Builder',    'Build strong legal arguments',             Color(0xFFF5A623)),
    (Icons.translate_outlined,      'Legal Translate',  'Simplify complex legal language',          Color(0xFFDB2777)),
    (Icons.checklist_rounded,       'Compliance Check', 'Review for regulatory issues',             Color(0xFF0A1628)),
  ];

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Hero banner ──
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [_DS.navy, _DS.blue],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: _DS.r12,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.auto_awesome_rounded,
                        color: _DS.gold, size: 20),
                    const SizedBox(width: 8),
                    Text('AI Legal Assistant',
                        style: _T.h2.copyWith(color: Colors.white)),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'Supercharge your legal practice with AI',
                  style: _T.bodySmall.copyWith(color: Colors.white60),
                ),
                const SizedBox(height: 16),
                // Ask anything teaser → navigates to ai-chat
                GestureDetector(
                  onTap: () => context.push('/ai-chat'),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: _DS.r20,
                      border: Border.all(color: Colors.white24),
                    ),
                    child: Row(
                      children: [
                        Text('Ask anything legal…',
                            style: _T.bodySmall
                                .copyWith(color: Colors.white54)),
                        const Spacer(),
                        const Icon(Icons.send_rounded,
                            color: Colors.white54, size: 18),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // ── Open AI Chat button ──
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              icon: const Icon(Icons.auto_awesome_outlined, size: 18),
              label: Text('Open AI Chat',
                  style: _T.h3.copyWith(color: Colors.white)),
              style: ElevatedButton.styleFrom(
                backgroundColor: _DS.blue,
                foregroundColor: Colors.white,
                elevation: 0,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: _DS.r12),
              ),
              onPressed: () => context.push('/ai-chat'),
            ),
          ),

          const SizedBox(height: 20),
          Text('AI Tools', style: _T.h2),
          const SizedBox(height: 12),

          // ── Tool grid ──
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              mainAxisSpacing: 10,
              crossAxisSpacing: 10,
              childAspectRatio: 1.25,
            ),
            itemCount: _tools.length,
            itemBuilder: (_, i) {
              final (icon, title, desc, color) = _tools[i];
              return _AIToolCard(
                  icon: icon, title: title, desc: desc, color: color);
            },
          ),
        ],
      ),
    );
  }
}

class _AIToolCard extends StatelessWidget {
  final IconData icon;
  final String title, desc;
  final Color color;
  const _AIToolCard(
      {required this.icon,
      required this.title,
      required this.desc,
      required this.color});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push('/ai-chat'),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: _DS.card,
          borderRadius: _DS.r12,
          boxShadow: _DS.cardShadow,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: _DS.r8,
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(height: 10),
            Text(title, style: _T.h3),
            const SizedBox(height: 3),
            Text(desc,
                style: _T.caption,
                maxLines: 2,
                overflow: TextOverflow.ellipsis),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────
//  INBOX VIEW
// ─────────────────────────────────────────────
class InboxView extends StatelessWidget {
  const InboxView({super.key});

  static const chats = [
    ('Rajesh Sharma', 'Regarding your case',   '10m', true),
    ('Priya Mehta',   'Consultation request',   '1h',  true),
    ('Amit Verma',    'Thanks for advice',      '3h',  false),
    ('Sunita Rao',    'Contract issue',         '1d',  false),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // ── Search bar ──
        Container(
          color: _DS.card,
          padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
          child: TextField(
            decoration: InputDecoration(
              hintText: 'Search messages…',
              hintStyle: _T.bodySmall,
              prefixIcon: const Icon(Icons.search_rounded,
                  color: _DS.textMuted, size: 20),
              filled: true,
              fillColor: _DS.surface,
              contentPadding: const EdgeInsets.symmetric(vertical: 10),
              border: OutlineInputBorder(
                borderRadius: _DS.r20,
                borderSide: BorderSide.none,
              ),
            ),
          ),
        ),
        Divider(height: 1, color: _DS.divider),

        // ── Chat list ──
        Expanded(
          child: ListView.separated(
            itemCount: chats.length,
            separatorBuilder: (_, __) =>
                Divider(height: 1, indent: 72, color: _DS.divider),
            itemBuilder: (_, i) {
              final (name, msg, time, unread) = chats[i];
              return _ChatTile(
                name: name,
                msg: msg,
                time: time,
                unread: unread,
              );
            },
          ),
        ),
      ],
    );
  }
}

class _ChatTile extends StatelessWidget {
  final String name, msg, time;
  final bool unread;
  const _ChatTile({
    required this.name,
    required this.msg,
    required this.time,
    required this.unread,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      leading: Stack(
        clipBehavior: Clip.none,
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: _DS.navy,
            child: Text(
              name[0],
              style: const TextStyle(
                  color: Colors.white, fontWeight: FontWeight.w700),
            ),
          ),
          if (unread)
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
      title: Text(
        name,
        style: _T.h3.copyWith(
          fontWeight: unread ? FontWeight.w700 : FontWeight.w500,
        ),
      ),
      subtitle: Text(
        msg,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: _T.bodySmall.copyWith(
          fontWeight: unread ? FontWeight.w600 : FontWeight.w400,
          color: unread ? _DS.textPrimary : _DS.textMuted,
        ),
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(time,
              style: _T.caption.copyWith(
                color: unread ? _DS.blue : _DS.textMuted,
                fontWeight:
                    unread ? FontWeight.w700 : FontWeight.w400,
              )),
          if (unread) ...[
            const SizedBox(height: 4),
            Container(
              width: 8,
              height: 8,
              decoration: const BoxDecoration(
                  color: _DS.blue, shape: BoxShape.circle),
            ),
          ],
        ],
      ),
      // ── ROUTE UNCHANGED ──
      onTap: () => context.push('/lawyer-to-client-chat'),
    );
  }
}

// ─────────────────────────────────────────────
//  DASHBOARD
// ─────────────────────────────────────────────
class LawyerDashboard extends ConsumerStatefulWidget {
  const LawyerDashboard({super.key});

  @override
  ConsumerState<LawyerDashboard> createState() =>
      _LawyerDashboardState();
}

class _LawyerDashboardState extends ConsumerState<LawyerDashboard> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    // ── Screen names / order UNCHANGED ──
    final screens = [
      const SocialFeed(),
      const InboxView(),
      const AIToolsView(),
      const LawyerProfileView(),
    ];

    return Scaffold(
      backgroundColor: _DS.surface,

      // ── AppBar ──
      appBar: AppBar(
        backgroundColor: _DS.navy,
        elevation: 0,
        title: Row(
          children: [
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: _DS.blue,
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Icon(Icons.balance_rounded,
                  color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            Text(
              l10n.lawyer,
              style: GoogleFonts.dmSans(
                color: Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 18,
                letterSpacing: -0.3,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search_rounded, color: Colors.white70),
            onPressed: () {},
          ),
          Stack(
            clipBehavior: Clip.none,
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined,
                    color: Colors.white70),
                onPressed: () {},
              ),
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                      color: _DS.gold, shape: BoxShape.circle),
                ),
              ),
            ],
          ),
          const SizedBox(width: 4),
        ],
      ),

      body: screens[_index],

      // ── Bottom Nav ──
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: _DS.card,
          border: Border(top: BorderSide(color: _DS.divider, width: 1)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 10,
              offset: const Offset(0, -3),
            ),
          ],
        ),
        child: SafeArea(
          top: false,
          child: Padding(
            padding:
                const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _navItem(Icons.home_rounded,        Icons.home_outlined,         'Feed',    0),
                _navItem(Icons.inbox_rounded,        Icons.inbox_outlined,        'Inbox',   1),
                _navItem(Icons.auto_awesome_rounded, Icons.auto_awesome_outlined, 'AI',      2),
                _navItem(Icons.person_rounded,       Icons.person_outline,        'Profile', 3),
              ],
            ),
          ),
        ),
      ),

      // ── FAB ──
      floatingActionButton: _index == 0
          ? FloatingActionButton.extended(
              backgroundColor: _DS.blue,
              foregroundColor: Colors.white,
              elevation: 3,
              icon: const Icon(Icons.edit_rounded, size: 18),
              label: Text('Post',
                  style: GoogleFonts.dmSans(
                      fontWeight: FontWeight.w600)),
              onPressed: () async {
                final created = await showDialog<bool>(
                  context: context,
                  builder: (_) => const _NewPostDialog(),
                );
                if (created == true && mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Post shared!', style: _T.body),
                      backgroundColor: _DS.success,
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                          borderRadius: _DS.r8),
                    ),
                  );
                }
              },
            )
          : null,
    );
  }

  Widget _navItem(
      IconData activeIcon, IconData idleIcon, String label, int i) {
    final isActive = _index == i;
    return GestureDetector(
      onTap: () => setState(() => _index = i),
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: EdgeInsets.symmetric(
          horizontal: isActive ? 16 : 12,
          vertical: 8,
        ),
        decoration: BoxDecoration(
          color: isActive ? _DS.blueLight : Colors.transparent,
          borderRadius: _DS.r20,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(isActive ? activeIcon : idleIcon,
                size: 22,
                color: isActive ? _DS.blue : _DS.textMuted),
            const SizedBox(height: 3),
            Text(
              label,
              style: GoogleFonts.dmSans(
                fontSize: 11,
                fontWeight:
                    isActive ? FontWeight.w700 : FontWeight.w500,
                color: isActive ? _DS.blue : _DS.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────
//  SOCIAL FEED
// ─────────────────────────────────────────────
class SocialFeed extends ConsumerWidget {
  const SocialFeed({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final posts = ref.watch(feedProvider);

    return ListView(
      padding: const EdgeInsets.only(top: 8, bottom: 100),
      children: [
        const _CreatePostCard(),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
          child: Row(
            children: [
              Text('Recent Posts',
                  style: _T.label.copyWith(letterSpacing: 0.5)),
              const SizedBox(width: 8),
              Expanded(
                  child: Divider(color: _DS.divider, height: 1)),
            ],
          ),
        ),
        ...posts.map((p) => FeedCard(post: p)),
      ],
    );
  }
}

// ── Create Post Card ─────────────────────────
class _CreatePostCard extends StatelessWidget {
  const _CreatePostCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _DS.card,
        borderRadius: _DS.r12,
        boxShadow: _DS.cardShadow,
      ),
      child: Column(
        children: [
          Row(
            children: [
              const CircleAvatar(
                radius: 20,
                backgroundColor: _DS.navy,
                child: Icon(Icons.person_rounded,
                    size: 20, color: Colors.white70),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: GestureDetector(
                  onTap: () => showDialog(
                    context: context,
                    builder: (_) => const _NewPostDialog(),
                  ),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 11),
                    decoration: BoxDecoration(
                      borderRadius: _DS.r20,
                      border: Border.all(
                          color: _DS.divider, width: 1.5),
                    ),
                    child: Text(
                      'Share an insight or update…',
                      style: _T.bodySmall,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _quickAction(Icons.photo_outlined,   'Photo',   _DS.success),
              _quickAction(Icons.article_outlined, 'Article', _DS.blue),
              _quickAction(Icons.event_outlined,   'Event',   _DS.gold),
            ],
          ),
        ],
      ),
    );
  }

  Widget _quickAction(IconData icon, String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 18, color: color),
        const SizedBox(width: 5),
        Text(label, style: _T.label.copyWith(color: color)),
      ],
    );
  }
}

// ── Feed Card ────────────────────────────────
class FeedCard extends ConsumerStatefulWidget {
  final FeedPost post;
  const FeedCard({super.key, required this.post});

  @override
  ConsumerState<FeedCard> createState() => _FeedCardState();
}

class _FeedCardState extends ConsumerState<FeedCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final controller = ref.read(feedProvider.notifier);
    final p = widget.post;
    final preview = p.content.length > 120 && !_expanded
        ? '${p.content.substring(0, 120)}…'
        : p.content;

    return Container(
      margin: const EdgeInsets.fromLTRB(12, 0, 12, 10),
      decoration: BoxDecoration(
        color: _DS.card,
        borderRadius: _DS.r12,
        boxShadow: _DS.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header ──
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 14, 14, 0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const CircleAvatar(
                  radius: 22,
                  backgroundColor: _DS.navy,
                  child: Icon(Icons.person_rounded,
                      size: 20, color: Colors.white70),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(p.author, style: _T.h3),
                      Text(p.title, style: _T.caption),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Text('2h ago', style: _T.caption),
                          const SizedBox(width: 4),
                          Icon(Icons.public,
                              size: 11, color: _DS.textMuted),
                        ],
                      ),
                    ],
                  ),
                ),
                // Follow pill
                _FollowButton(
                  following: p.following,
                  onTap: () => controller.toggleFollow(p.id),
                ),
              ],
            ),
          ),

          // ── Content ──
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 10, 14, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(preview,
                    style: _T.body.copyWith(height: 1.5)),
                if (p.content.length > 120)
                  GestureDetector(
                    onTap: () =>
                        setState(() => _expanded = !_expanded),
                    child: Text(
                      _expanded ? ' show less' : ' …see more',
                      style: GoogleFonts.dmSans(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: _DS.blue),
                    ),
                  ),
              ],
            ),
          ),

          // ── Reaction summary ──
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 10, 14, 4),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: _DS.blueLight,
                    borderRadius: _DS.rFull,
                  ),
                  child: const Text('👍',
                      style: TextStyle(fontSize: 13)),
                ),
                const Spacer(),
                Text('${p.likes} reactions', style: _T.caption),
              ],
            ),
          ),

          Divider(height: 1, color: _DS.divider),

          // ── Actions ──
          Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: 4, vertical: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _actionBtn(
                  icon: p.liked
                      ? Icons.thumb_up_rounded
                      : Icons.thumb_up_alt_outlined,
                  label: 'Like',
                  color: p.liked ? _DS.blue : _DS.textSecondary,
                  onTap: () => controller.toggleLike(p.id),
                ),
                _actionBtn(
                  icon: Icons.chat_bubble_outline_rounded,
                  label: 'Comment',
                  color: _DS.textSecondary,
                  onTap: () {},
                ),
                _actionBtn(
                  icon: Icons.repeat_rounded,
                  label: 'Repost',
                  color: _DS.textSecondary,
                  onTap: () {},
                ),
                _actionBtn(
                  icon: Icons.send_outlined,
                  label: 'Send',
                  color: _DS.textSecondary,
                  onTap: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _actionBtn({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: _DS.r8,
      child: Padding(
        padding: const EdgeInsets.symmetric(
            horizontal: 10, vertical: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18, color: color),
            const SizedBox(width: 5),
            Text(label,
                style: _T.bodySmall.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _FollowButton extends StatelessWidget {
  final bool following;
  final VoidCallback onTap;
  const _FollowButton(
      {required this.following, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(
            horizontal: 14, vertical: 6),
        decoration: BoxDecoration(
          color: following ? _DS.blueLight : Colors.transparent,
          borderRadius: _DS.rFull,
          border: Border.all(color: _DS.blue),
        ),
        child: Text(
          following ? '✓ Following' : '+ Follow',
          style: _T.label.copyWith(
              color: _DS.blue, fontSize: 13),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────
//  NEW POST DIALOG
// ─────────────────────────────────────────────
class _NewPostDialog extends StatefulWidget {
  const _NewPostDialog();

  @override
  State<_NewPostDialog> createState() => _NewPostDialogState();
}

class _NewPostDialogState extends State<_NewPostDialog> {
  final _titleCtrl = TextEditingController();
  final _bodyCtrl  = TextEditingController();

  @override
  void dispose() {
    _titleCtrl.dispose();
    _bodyCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: _DS.r12),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const CircleAvatar(
                  radius: 18,
                  backgroundColor: _DS.navy,
                  child: Icon(Icons.person_rounded,
                      size: 18, color: Colors.white70),
                ),
                const SizedBox(width: 10),
                Text('Create a post', style: _T.h2),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close_rounded, size: 20),
                  onPressed: () => Navigator.pop(context, false),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _titleCtrl,
              style: _T.body,
              decoration: InputDecoration(
                hintText: 'Add a title…',
                hintStyle: _T.bodySmall,
                filled: true,
                fillColor: _DS.surface,
                border: OutlineInputBorder(
                  borderRadius: _DS.r8,
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _bodyCtrl,
              style: _T.body,
              maxLines: 4,
              decoration: InputDecoration(
                hintText:
                    'Share an insight, achievement, or update…',
                hintStyle: _T.bodySmall,
                filled: true,
                fillColor: _DS.surface,
                border: OutlineInputBorder(
                  borderRadius: _DS.r8,
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.photo_outlined,
                      color: _DS.textSecondary),
                  onPressed: () {},
                ),
                IconButton(
                  icon: const Icon(Icons.link_rounded,
                      color: _DS.textSecondary),
                  onPressed: () {},
                ),
                const Spacer(),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _DS.blue,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: _DS.r20),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 24, vertical: 12),
                  ),
                  onPressed: () => Navigator.pop(context, true),
                  child: Text('Post',
                      style:
                          _T.h3.copyWith(color: Colors.white)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}