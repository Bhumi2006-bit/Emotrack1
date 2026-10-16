// frontend/src/services/demoData.js
// Pre-seeded high quality sample data for fail-safe Demo Mode and immediate visualization

export const DEMO_USER = {
  id: 1,
  username: "demo_preview",
  name: "Demo",
  email: "demo@emotrack.ai",
  streak_days: 5,
  created_at: "September 2026",
  total_analyses: 24,
};

export const DEMO_DASHBOARD = {
  user_name: "Demo",
  streak_days: 5,
  total_entries: 24,
  wellness: {
    score: 72,
    status: "Balanced",
    change_pct: 8,
    direction: "up",
    message: "Your recent entries indicate a relatively stable wellness pattern."
  },
  emotion: {
    label: "Joy",
    confidence: 91
  },
  stress: {
    level: "Low",
    confidence: 87
  },
  weekly_trend: [
    { day: "Mon", score: 52 },
    { day: "Tue", score: 58 },
    { day: "Wed", score: 55 },
    { day: "Thu", score: 63 },
    { day: "Fri", score: 68 },
    { day: "Sat", score: 72 }
  ],
  emotion_distribution: [
    { emotion: "Joy", percentage: 42, color: "#10B981" },
    { emotion: "Neutral", percentage: 28, color: "#64748B" },
    { emotion: "Sadness", percentage: 12, color: "#3B82F6" },
    { emotion: "Fear", percentage: 7, color: "#F59E0B" },
    { emotion: "Anger", percentage: 6, color: "#EF4444" },
    { emotion: "Surprise", percentage: 3, color: "#8B5CF6" },
    { emotion: "Disgust", percentage: 2, color: "#0D9488" }
  ]
};

export const DEMO_HISTORY = [
  {
    id: 104,
    created_at: "Today · 8:42 PM",
    date: "Sep 23",
    input_text: "I finally finished my project submission and feel really relieved. The team collaborated well and we overcame the stubborn bugs in the pipeline.",
    primary_emotion: "Joy",
    emotion_confidence: 0.94,
    emotion_distribution: { Joy: 0.94, Neutral: 0.03, Surprise: 0.015, Sadness: 0.005, Fear: 0.004, Anger: 0.003, Disgust: 0.003 },
    stress_level: "Low",
    stress_confidence: 0.88,
    wellness_score: 78,
    wellness_status: "Positive Pattern",
    trend_direction: "Improving",
    trend_entries: 24,
    insight: "Completion of high-effort milestones consistently correlates with marked elevation in your wellness indicator.",
    recommendations: [
      "Celebrate this milestone with an intentional rest period.",
      "Take a walk to let your body unwind after intense focus.",
      "Acknowledge the effort you put in."
    ],
    context_signals: [
      { word: "finally finished", weight: 0.92 },
      { word: "relieved", weight: 0.88 },
      { word: "collaborated", weight: 0.81 }
    ]
  },
  {
    id: 103,
    created_at: "Yesterday · 6:15 PM",
    date: "Sep 22",
    input_text: "I have so much work left and I'm worried about tomorrow's presentation. Feeling the pressure build up as the time draws near.",
    primary_emotion: "Fear",
    emotion_confidence: 0.89,
    emotion_distribution: { Fear: 0.89, Sadness: 0.05, Neutral: 0.03, Anger: 0.015, Joy: 0.008, Surprise: 0.004, Disgust: 0.003 },
    stress_level: "High",
    stress_confidence: 0.91,
    wellness_score: 42,
    wellness_status: "Needs Attention",
    trend_direction: "Needs Attention",
    trend_entries: 23,
    insight: "Upcoming public speaking and evaluative deadlines repeatedly trigger transient spikes in perceived urgency.",
    recommendations: [
      "Practice a 5-minute box breathing cycle to steady your autonomic response.",
      "Rehearse only the first 2 minutes of your talk.",
      "Remind yourself of past successful presentations."
    ],
    context_signals: [
      { word: "worried", weight: 0.91 },
      { word: "pressure build up", weight: 0.87 },
      { word: "so much work", weight: 0.74 }
    ]
  },
  {
    id: 102,
    created_at: "Sep 21 · 2:30 PM",
    date: "Sep 21",
    input_text: "Quiet, productive morning reviewing research papers and organizing notes.",
    primary_emotion: "Neutral",
    emotion_confidence: 0.85,
    emotion_distribution: { Neutral: 0.85, Joy: 0.08, Sadness: 0.03, Fear: 0.02, Surprise: 0.01, Anger: 0.005, Disgust: 0.005 },
    stress_level: "Moderate",
    stress_confidence: 0.78,
    wellness_score: 64,
    wellness_status: "Balanced",
    trend_direction: "Stable",
    trend_entries: 22,
    insight: "Quiet, structured mornings serve as a stabilizing anchor across your weekly reflections.",
    recommendations: [
      "Maintain this calm pacing throughout the rest of your day.",
      "Hydrate and stretch before your next task."
    ],
    context_signals: [
      { word: "quiet", weight: 0.82 },
      { word: "productive", weight: 0.79 }
    ]
  },
  {
    id: 101,
    created_at: "Sep 20 · 9:10 PM",
    date: "Sep 20",
    input_text: "Feeling a bit drained and sluggish today. Nothing went wrong, just feeling flat.",
    primary_emotion: "Sadness",
    emotion_confidence: 0.76,
    emotion_distribution: { Sadness: 0.76, Neutral: 0.16, Fear: 0.03, Joy: 0.02, Anger: 0.015, Surprise: 0.01, Disgust: 0.005 },
    stress_level: "Moderate",
    stress_confidence: 0.74,
    wellness_score: 51,
    wellness_status: "Balanced",
    trend_direction: "Stable",
    trend_entries: 21,
    insight: "Periods of low physiological energy appear after high-focus exertion cycles.",
    recommendations: [
      "Allow yourself an early night without guilt.",
      "Keep tonight's to-do list minimal."
    ],
    context_signals: [
      { word: "drained", weight: 0.85 },
      { word: "sluggish", weight: 0.78 }
    ]
  }
];

export const DEMO_PRESETS = [
  {
    title: "Exam & Deadline Concern",
    text: "I've been really worried about my exams lately. I know I've prepared but I still feel like something will go wrong and time is running out."
  },
  {
    title: "Project Milestone Relief",
    text: "I finally finished my project submission and feel really relieved. The team celebrated over chai and I'm proud of what we accomplished."
  },
  {
    title: "Quiet Study Rhythm",
    text: "Had a steady study session today. Kept things organized, took regular breaks, and felt peaceful throughout the afternoon."
  }
];

export const DEMO_RECOMMENDATIONS_CATALOG = {
  calm: [
    {
      title: "Short Grounding Exercise (5-4-3-2-1)",
      desc: "Identify 5 things you can see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste to re-center in the present moment.",
      badge: "Sensory Grounding",
      time: "3 mins"
    },
    {
      title: "Gentle Box Breathing",
      desc: "Inhale 4 seconds, hold 4 seconds, exhale 4 seconds, hold 4 seconds. Restores autonomic equilibrium during anxiety spikes.",
      badge: "Breathwork",
      time: "5 mins"
    },
    {
      title: "Tactile Mindful Pause",
      desc: "Step completely away from your desk. Wash your hands with cool water and feel the physical sensations without checking notifications.",
      badge: "Physical Reset",
      time: "2 mins"
    }
  ],
  academic: [
    {
      title: "Task Slicing (Micro-Milestone)",
      desc: "Break an overwhelming syllabus or chapter into a single 15-minute slice. Commit only to that slice without looking ahead.",
      badge: "Workload Triage",
      time: "15 mins"
    },
    {
      title: "Single-Focus Sprint",
      desc: "Turn off all message notifications and tackle one question or paragraph with a timer. Stop cleanly when the bell rings.",
      badge: "Deep Focus",
      time: "20 mins"
    },
    {
      title: "Cognitive Offloading",
      desc: "Write every worry or pending item onto a scratch paper to empty your working memory before starting to study.",
      badge: "De-clutter",
      time: "5 mins"
    }
  ],
  routine: [
    {
      title: "Screen Curfew Window",
      desc: "Put laptops and smartphones into another room 30 minutes before bed to allow melatonin production to normalize.",
      badge: "Circadian Care",
      time: "30 mins"
    },
    {
      title: "Quiet Evening Stroll",
      desc: "Take an unhurried 15-minute walk outside without headphones. Let your gaze wander to horizon lines.",
      badge: "Decompression",
      time: "15 mins"
    },
    {
      title: "Consistent Sleep Rhythm",
      desc: "Protect a regular sleep schedule even during exam weeks. Brain consolidation requires adequate non-REM cycles.",
      badge: "Restorative Rest",
      time: "7-8 hrs"
    }
  ]
};
