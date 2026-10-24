import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSessionStore } from '../stores/session'

describe('Session Store End-to-End Flow (guest → quiz → results)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('initializes with default Grade 5 Georgia Fractions', () => {
    const session = useSessionStore()
    expect(session.board).toBe('georgia')
    expect(session.grade).toBe(5)
    expect(session.topic).toBe('fractions')
    expect(session.tier).toBe('medium')
    expect(session.score).toBe(0)
    expect(session.streak).toBe(0)
  })

  it('records answers correctly, updating score, streak, and round records', () => {
    const session = useSessionStore()
    const mockQuestion = {
      id: 'q-101',
      grade: 5,
      topic: 'fractions',
      tier: 'medium' as const,
      stem: 'What is 1/2 + 1/4?',
      expression: '1/2 + 1/4',
      options: [
        { id: 'A', text: '3/4' },
        { id: 'B', text: '2/6' },
      ],
      correct_option_id: 'A',
      explanation: 'Find LCD = 4: 2/4 + 1/4 = 3/4',
      standard_code: 'MGSE5.NF.1',
    }

    // Answer 1: Correct (+20 XP)
    session.recordAnswer(
      {
        is_correct: true,
        points: 20,
        streak: 1,
        new_mastery: 56.0,
        next_tier: 'medium',
        new_badges: ['First Steps'],
      },
      mockQuestion,
      'A'
    )

    expect(session.score).toBe(20)
    expect(session.streak).toBe(1)
    expect(session.bestStreak).toBe(1)
    expect(session.mastery['fractions']).toBe(56.0)
    expect(session.badges).toContain('First Steps')
    expect(session.roundRecords).toHaveLength(1)
    expect(session.roundAccuracyPercent).toBe(100)

    // Answer 2: Incorrect (0 XP, streak reset)
    session.recordAnswer(
      {
        is_correct: false,
        points: 0,
        streak: 0,
        new_mastery: 52.0,
        next_tier: 'easy',
        misconception_tag: 'add_numerators_add_denominators',
        misconception_feedback: 'Added across without finding common denominator',
      },
      mockQuestion,
      'B'
    )

    expect(session.score).toBe(20)
    expect(session.streak).toBe(0)
    expect(session.bestStreak).toBe(1) // preserved!
    expect(session.roundRecords).toHaveLength(2)
    expect(session.roundCorrectCount).toBe(1)
    expect(session.roundAccuracyPercent).toBe(50)
  })

  it('computes lowestMasteryTopic correctly to guide adaptive recommendations', () => {
    const session = useSessionStore()
    session.mastery['fractions'] = 80
    session.mastery['decimals'] = 35 // Lowest!
    session.mastery['geometry'] = 60
    session.mastery['ratios'] = 70

    const lowest = session.lowestMasteryTopic
    expect(lowest.id).toBe('decimals')
    expect(lowest.score).toBe(35)
  })

  it('generates continueAdventureCard based on recent activity', () => {
    const session = useSessionStore()
    session.addActivity({
      topic: 'geometry',
      board: 'georgia',
      grade: 5,
      tier: 'hard',
      score: 150,
      accuracy_percent: 90,
      correct_count: 9,
      total_questions: 10,
      created_at: new Date().toISOString(),
    })

    const continueCard = session.continueAdventureCard
    expect(continueCard.topic).toBe('geometry')
    expect(continueCard.tier).toBe('hard')
    expect(continueCard.grade).toBe(5)
  })

  it('resetAllProgress clears all accumulated scores, streaks, history, and badges', () => {
    const session = useSessionStore()
    session.score = 500
    session.streak = 5
    session.bestStreak = 8
    session.badges = ['First Steps', '5-Streak']
    session.recentActivities = [{ topic: 'fractions', score: 100 } as any]

    session.resetAllProgress()

    expect(session.score).toBe(0)
    expect(session.streak).toBe(0)
    expect(session.bestStreak).toBe(0)
    expect(session.badges).toHaveLength(0)
    expect(session.recentActivities).toHaveLength(0)
    expect(session.mastery['fractions']).toBe(50.0)
  })
})
