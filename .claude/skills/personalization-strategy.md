---
name: personalization-strategy
description: Design user-adaptive content personalization strategies for educational platforms. Use when implementing chapter-level or response-level content adaptation based on user profiles, learning styles, or background knowledge.
---

# Skill: Personalization Strategy

**Version**: 1.0.0
**Created**: 2025-11-28
**Category**: User Experience
**Decision Points**: 4

## Description

This skill provides a framework for designing content personalization strategies that adapt educational material to user background, proficiency level, and learning preferences. It balances personalization depth with implementation complexity and performance.

## When to Use This Skill

**Apply this skill when:**
- Implementing "Personalize this chapter" features in educational content
- Designing user onboarding flows that collect profile information
- Building adaptive AI tutors that adjust explanation depth
- Creating content variants for different audience segments (beginner/advanced)
- Optimizing LLM prompts based on user context

**Skip this skill when:**
- Content is inherently one-size-fits-all (reference documentation, API specs)
- User base is homogeneous (all users have same background)
- Personalization overhead exceeds benefit (tiny content corpus, no observed variability in needs)
- Performance constraints prohibit dynamic content generation

## Persona

You are a UX designer thinking about personalization the way a teacher thinks about differentiated instruction:

- **User segmentation**: What dimensions of user background meaningfully affect content needs?
- **Adaptation gradients**: How should content vary across user segments? (depth, examples, prerequisites)
- **Performance trade-offs**: What's cached vs generated on-demand?
- **Validation strategy**: How to measure if personalization improves learning outcomes?

Your goal: Design personalization that genuinely improves user experience without over-engineering or hurting performance.

## Analytical Questions

Before implementing personalization, analyze:

### 1. **User Profile Dimensions**
- What aspects of user background affect content needs? (technical level, hardware access, learning goals, language)
- Which dimensions are most impactful? (80/20 rule: focus on high-impact factors)
- How to collect profile data? (signup questionnaire, inferred from behavior, explicit preferences)
- What are the discrete user segments? (beginner/intermediate/advanced, simulation-only/hardware-access)

### 2. **Content Variation Strategy**
- How should content adapt for each segment? (depth of explanation, example complexity, prerequisite coverage)
- What content elements are personalized? (text, code examples, diagrams, exercises)
- What stays constant across segments? (core concepts, learning objectives, assessment criteria)
- How much variation is meaningful? (avoid token differences that don't affect comprehension)

### 3. **Caching vs Dynamic Generation**
- What's the performance budget for personalization? (max latency tolerable)
- What content can be pre-generated and cached? (finite segments × chapters)
- What must be generated dynamically? (user-specific queries, conversational context)
- What's the cache invalidation strategy? (when content updates, profiles change)

### 4. **Validation & Metrics**
- How to measure personalization effectiveness? (engagement, comprehension, completion rates)
- What baseline to compare against? (non-personalized version)
- What's the minimum effect size to justify complexity? (e.g., 10% improvement in quiz scores)
- How to A/B test personalization variants?

## Decision Principles

Apply these frameworks when designing personalization:

### 1. **User Segmentation Framework**

**High-Impact Dimensions** (personalize on these):
```
1. Technical Background (Software Proficiency)
   - Beginner: No programming experience, needs step-by-step explanations
   - Intermediate: Knows Python basics, can understand code with comments
   - Advanced: Experienced developer, wants concise explanations and advanced patterns

2. Hardware Access
   - Simulation-only: No physical robots, needs simulation-focused examples
   - Edge kit access: Has compute module, can run edge deployments
   - Full lab access: Has complete robotics hardware, can run all examples

3. Learning Goal
   - Conceptual understanding: Wants theory and intuition
   - Practical implementation: Wants code and step-by-step guides
   - Research/advanced: Wants papers, optimization techniques, cutting-edge topics
```

**Low-Impact Dimensions** (don't over-optimize):
```
- Learning style preferences (visual/auditory/kinesthetic) - weak evidence of impact
- Personality types - not actionable for content adaptation
- Demographic attributes - avoid assumptions based on age/location/gender
```

**Principle**: Focus personalization on factors with measurable impact on learning outcomes. Ignore buzzwords without evidence.

### 2. **Content Adaptation Patterns**

**Pattern A: Explanation Depth Variation**

```markdown
# CORE CONTENT (All users see this)
## What is a ROS2 Publisher?
A publisher sends messages to a topic that other nodes can subscribe to.

# BEGINNER VARIANT
Think of it like a radio station: the publisher broadcasts messages on a channel (topic),
and anyone tuned to that channel (subscribers) receives the messages. You don't need
to know who's listening—just broadcast.

**Analogy**: If you've used print() in Python to show messages, a publisher is similar,
but instead of printing to your screen, it sends messages to other programs.

# INTERMEDIATE VARIANT
Publishers implement the pub-sub pattern you may have seen in message queues or event systems.
The publisher is decoupled from subscribers—it doesn't know or care who's listening.

# ADVANCED VARIANT
Under the hood, ROS2 publishers use DDS (Data Distribution Service) for discovery and transport.
Quality of Service (QoS) settings control reliability, durability, and history depth.
For high-throughput scenarios, consider BEST_EFFORT QoS over RELIABLE to reduce latency.
```

**Principle**: Core content is always present. Variants ADD context/depth, not replace core material.

**Pattern B: Example Complexity Variation**

```python
# BEGINNER VARIANT: Simple, heavily commented, single-purpose
import rclpy
from std_msgs.msg import String

def main():
    rclpy.init()
    node = rclpy.create_node('simple_publisher')

    # Create a publisher that sends String messages to 'topic'
    publisher = node.create_publisher(String, 'topic', 10)

    # Create a message and publish it
    msg = String()
    msg.data = 'Hello ROS2!'
    publisher.publish(msg)

    node.destroy_node()
    rclpy.shutdown()

# INTERMEDIATE VARIANT: Class-based, timer-driven, best practices
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class HelloPublisher(Node):
    def __init__(self):
        super().__init__('hello_publisher')
        self.publisher = self.create_publisher(String, 'topic', 10)
        self.timer = self.create_timer(1.0, self.publish_message)
        self.counter = 0

    def publish_message(self):
        msg = String()
        msg.data = f'Hello ROS2! Count: {self.counter}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')
        self.counter += 1

def main():
    rclpy.init()
    node = HelloPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

# ADVANCED VARIANT: QoS tuning, lifecycle management, type hints
from typing import Optional
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String

class OptimizedPublisher(Node):
    def __init__(self) -> None:
        super().__init__('optimized_publisher')

        # Custom QoS for high-throughput scenarios
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,  # Lower latency
            history=HistoryPolicy.KEEP_LAST,
            depth=1  # Don't buffer old messages
        )

        self.publisher = self.create_publisher(String, 'topic', qos_profile)
        self.timer = self.create_timer(0.01, self.publish_callback)  # 100 Hz

    def publish_callback(self) -> None:
        msg = String(data=f'High-freq message: {self.get_clock().now()}')
        self.publisher.publish(msg)
```

**Principle**: Beginner code is runnable and teaches one concept. Advanced code shows production patterns and optimizations.

**Pattern C: Prerequisite Coverage Variation**

```markdown
# BEGINNER VARIANT (Assumes no prior knowledge)
Before we dive into ROS2 nodes, let's make sure you understand these Python basics:

**What is a class?** A class is a blueprint for creating objects...
**What is an import?** Import statements let you use code from other files...
**What is a function?** A function is a reusable block of code...

[Full prerequisite review section]

# INTERMEDIATE VARIANT (Brief reminder)
**Quick refresher**: ROS2 nodes are Python classes that inherit from `rclpy.node.Node`.
If you need a deeper review of Python classes, see Chapter 2.

# ADVANCED VARIANT (Reference only)
Prerequisites: Python OOP, async/await patterns, pub-sub architecture familiarity.
```

**Principle**: Don't waste advanced users' time with basics. Don't lose beginners by assuming knowledge.

### 3. **Caching Strategy Framework**

**Pre-Generated Caching** (Fast, storage-intensive):
```
Use when:
✅ Finite user segments (3-5 levels)
✅ Static content (chapters don't change frequently)
✅ Performance is critical (p95 < 100ms)

Implementation:
- Generate all variants at build time: 13 chapters × 3 levels = 39 cached versions
- Store in database/CDN with key: chapter_id + user_level
- Serve instantly on page load

Cost: 39 × 10KB avg ≈ 390KB storage (negligible)
```

**Dynamic Generation** (Slow, flexible):
```
Use when:
✅ Infinite personalization dimensions (user-specific queries)
✅ Conversational context (chat messages)
✅ Real-time adaptation (based on current session behavior)

Implementation:
- LLM prompt includes user profile: "Explain X for a beginner with no Python experience"
- Generate on-demand, cache for session duration
- Expire cache after 1 hour or profile update

Cost: ~2 seconds latency per generation, $0.001 per query (OpenAI)
```

**Hybrid Strategy** (Optimal):
```
Chapter Content: Pre-generated (3 variants per chapter, served instantly)
Chat Responses: Dynamic (personalized to exact user query and context)
Code Examples: Pre-generated (stored in chapter variants)
Exercises: Dynamic (LLM generates personalized follow-up questions)
```

**Principle**: Cache what's predictable (finite segments), generate what's contextual (user-specific queries).

### 4. **Validation Metrics Framework**

**Engagement Metrics**:
```
- Time on page: Personalized vs baseline (expect 10-20% increase)
- Scroll depth: % of page viewed (expect higher completion rate)
- Bounce rate: % leaving immediately (expect 5-10% decrease)
```

**Comprehension Metrics**:
```
- Quiz scores: End-of-chapter assessments (expect 10-15% improvement)
- Exercise completion: % completing hands-on tasks (expect 15-20% improvement)
- Help requests: Support tickets/questions (expect 20% decrease for beginners)
```

**User Satisfaction**:
```
- Explicit feedback: "Was this personalization helpful?" thumbs up/down
- Net Promoter Score: Likelihood to recommend (expect +5 to +10 point improvement)
- Personalization opt-out rate: % disabling feature (should be <10%)
```

**A/B Testing Setup**:
```python
# Randomly assign users to control (no personalization) or treatment (personalized)
user.cohort = random.choice(['control', 'treatment'])

if user.cohort == 'treatment':
    content = get_personalized_content(chapter_id, user.profile)
else:
    content = get_default_content(chapter_id)

# Track metrics per cohort
analytics.track('chapter_view', {
    'chapter_id': chapter_id,
    'cohort': user.cohort,
    'user_level': user.profile.level,
    'time_on_page': time_spent,
    'quiz_score': quiz_result
})
```

**Principle**: Personalization must improve measurable outcomes. If no improvement after 100+ users, simplify or remove.

## Usage Example

**Scenario**: Design personalization for "Personalize this chapter" button in Physical AI textbook

**Invocation**:
```
I want to add a "Personalize this chapter" button at the start of each chapter.
When clicked, users see content adapted to their background (collected during signup).

Use the personalization-strategy skill to design this feature.

Context:
- Signup collects: software_level (beginner/intermediate/advanced), hardware_access (simulation-only/edge-kit/full-lab)
- 13 chapters of content, each 5-10 pages
- Users are reading in Docusaurus (static site)
- Performance budget: Page load <500ms (personalized content should not delay significantly)
- Implementation: Can pre-generate variants or use LLM for dynamic generation
```

**Expected Strategy**:

```markdown
## Personalization Strategy: Chapter-Level Adaptation

### 1. User Segmentation
**Primary Dimension**: software_level (beginner/intermediate/advanced)
**Secondary Dimension**: hardware_access (affects example selection)

**Rationale**: Software level has highest impact on explanation depth and prerequisite needs. Hardware access affects which code examples are runnable for the user.

### 2. Content Adaptation
**What Varies**:
- Explanation depth (beginner gets analogies, advanced gets theory)
- Code example complexity (beginner: simple scripts, advanced: production patterns)
- Prerequisite coverage (beginner gets full review, advanced gets references)

**What Stays Constant**:
- Core concepts and learning objectives
- Chapter structure and navigation
- Assessment questions (adapt difficulty in exercises, not quizzes)

### 3. Caching Strategy: Pre-Generation
**Approach**: Generate 3 variants per chapter at build time

```
Variants:
1. chapter-1-beginner.md
2. chapter-1-intermediate.md
3. chapter-1-advanced.md

Total: 13 chapters × 3 levels = 39 markdown files
Storage: ~500KB total (negligible)
Serve time: <50ms (instant)
```

**Implementation**:
```jsx
// Docusaurus component
function PersonalizedChapter({ chapterId }) {
  const user = useUserProfile();  // From auth context
  const level = user.software_level || 'intermediate';  // Default fallback

  // Load pre-generated variant
  const content = require(`./chapters/${chapterId}-${level}.md`);

  return <MDXProvider>{content}</MDXProvider>;
}
```

**Regeneration**: Run generation script on content updates (CI/CD hook)

### 4. Validation Metrics
**Primary Metric**: Quiz scores (expect 10-15% improvement for beginners)
**Secondary Metrics**:
- Time on page (expect 15% increase - more engaged)
- Chapter completion rate (expect 10% increase)
- "Personalization helpful?" feedback (target 80% positive)

**A/B Test Setup**:
- 50% of new users: See personalized content
- 50% of new users: See default (intermediate) content
- Track for 2 weeks, minimum 100 users per cohort

**Success Criteria**: If beginner cohort shows 10%+ improvement in quiz scores AND positive feedback >75%, roll out to 100%.

### 5. Implementation Plan
1. **Week 1**: Generate 3 variants for Chapter 1 manually, test quality
2. **Week 2**: Build automated generation script (LLM prompt: "Adapt this chapter for [level]")
3. **Week 3**: Generate all 39 variants, review for consistency
4. **Week 4**: Deploy with A/B test, monitor metrics
5. **Week 5**: Analyze results, iterate or roll out

**Estimated Effort**: 2-3 weeks
**Estimated Cost**: $5-10 for LLM generation (one-time)
**Performance Impact**: None (pre-generated, served from CDN)
```

## Self-Check Validation

After applying this skill, verify:

- [ ] **User segments are evidence-based**: Dimensions correlate with observed user needs or learning outcomes
- [ ] **Adaptation is meaningful**: Variants differ in comprehension-relevant ways (not cosmetic changes)
- [ ] **Performance is acceptable**: Personalization doesn't degrade page load times beyond budget
- [ ] **Validation plan exists**: Metrics defined to measure if personalization improves outcomes
- [ ] **Fallback strategy**: Non-personalized content works if profile is missing or generation fails

## Common Pitfalls

### Pitfall: Over-Segmentation
**Problem**: Creating 10+ user segments based on weak signals (learning style, timezone, device type)
**Fix**: Focus on 2-3 high-impact dimensions. More segments = more complexity, not better outcomes.

### Pitfall: Cosmetic Personalization
**Problem**: Changing colors or greetings but not educational content
**Fix**: Personalize substance (explanation depth, examples, prerequisites), not superficial elements.

### Pitfall: Performance Regression
**Problem**: Dynamic LLM generation adds 2-3 second latency on every page load
**Fix**: Pre-generate finite variants, reserve dynamic generation for truly user-specific content (chat).

### Pitfall: No Validation
**Problem**: Assuming personalization helps without measuring outcomes
**Fix**: A/B test with clear metrics. If no improvement, simplify or remove personalization.

---

**Key Principle**: Personalization is a means to an end (better learning outcomes), not an end itself. If simple is good enough, don't add complexity.
