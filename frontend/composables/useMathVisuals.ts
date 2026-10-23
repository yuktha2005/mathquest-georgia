/**
 * Composable providing:
 * 1. Automatic mathematical diagram parser for SVG visual models (FractionBar, NumberLine, ShapeDiagram)
 * 2. 3-Level progressive hint ladder generator (Nudge, Step, Worked Solution)
 */

export interface FractionVisualData {
  type: 'fraction'
  numerator: number
  denominator: number
  secondaryNumerator?: number
}

export interface NumberLineVisualData {
  type: 'number_line'
  startVal: number
  endVal: number
  min?: number
  max?: number
}

export interface ShapeVisualData {
  type: 'shape'
  shape: 'rectangle' | 'square' | 'triangle'
  width: number
  height: number
  unit: string
  highlight: 'area' | 'perimeter'
}

export type MathVisualData = FractionVisualData | NumberLineVisualData | ShapeVisualData | null

export interface HintLevel {
  level: 1 | 2 | 3
  title: string
  cost: number
  text: string
}

export const useMathVisuals = () => {
  /**
   * Parse an expression and question metadata to detect which SVG visual diagram to render.
   */
  const parseMathVisual = (
    expression: string,
    topic: string,
    stem: string = ''
  ): MathVisualData => {
    const expr = (expression || '').trim()
    const top = (topic || '').toLowerCase()
    const s = (stem || '').toLowerCase()

    // 1. Geometry Detection
    if (top === 'geometry' || s.includes('area') || s.includes('perimeter') || s.includes('rectangle') || s.includes('triangle')) {
      const isTriangle = s.includes('triangle') || expr.includes('/ 2') || expr.includes('÷ 2')
      const isPerimeter = s.includes('perimeter') || (expr.includes('+') && !expr.includes('*'))

      // Match numbers: e.g. "6 * 4" or "8 * 5 / 2" or "5 + 5 + 4 + 4"
      const nums = (expr.match(/\d+(\.\d+)?/g) || []).map(Number)
      if (nums.length >= 2) {
        return {
          type: 'shape',
          shape: isTriangle ? 'triangle' : 'rectangle',
          width: nums[0] || 6,
          height: nums[1] || 4,
          unit: s.includes('meter') ? 'm' : s.includes('yard') ? 'yd' : s.includes('cm') ? 'cm' : 'units',
          highlight: isPerimeter ? 'perimeter' : 'area',
        }
      }
    }

    // 2. Fractions Detection
    // Regex looking for a/b fractions
    const fractionMatches = [...expr.matchAll(/(\d+)\/(\d+)/g)]
    if (fractionMatches.length > 0) {
      const n1 = parseInt(fractionMatches[0][1], 10)
      const d1 = parseInt(fractionMatches[0][2], 10)
      let n2 = 0

      if (fractionMatches.length > 1 && expr.includes('+')) {
        n2 = parseInt(fractionMatches[1][1], 10)
      }

      return {
        type: 'fraction',
        numerator: n1,
        denominator: d1,
        secondaryNumerator: n2 > 0 ? n2 : undefined,
      }
    }

    // 3. Decimals / Number Line Detection
    // Matches e.g. "4.5 + 0.35" or "5.2 - 1.1"
    const decimalMatch = expr.match(/(\d+\.?\d*)\s*([+\-−])\s*(\d+\.?\d*)/)
    if (decimalMatch && (expr.includes('.') || top === 'decimals')) {
      const v1 = parseFloat(decimalMatch[1])
      const op = decimalMatch[2]
      const v2 = parseFloat(decimalMatch[3])
      const endVal = op === '+' ? v1 + v2 : v1 - v2

      return {
        type: 'number_line',
        startVal: v1,
        endVal: Number(endVal.toFixed(2)),
      }
    }

    return null
  }

  /**
   * Generates a 3-level progressive hint ladder:
   * Level 1: Nudge (conceptual pointer)
   * Level 2: Step (actionable procedural instruction)
   * Level 3: Worked Solution (full calculation breakdown)
   */
  const generateHintLadder = (
    expression: string,
    topic: string,
    stem: string = ''
  ): [HintLevel, HintLevel, HintLevel] => {
    const expr = (expression || '').trim()
    const top = (topic || '').toLowerCase()
    const s = (stem || '').toLowerCase()

    // 1. Fractions
    if (top.includes('fraction') || expr.includes('/')) {
      return [
        {
          level: 1,
          title: 'Level 1: Nudge',
          cost: 5,
          text: 'Look at the denominators (the bottom numbers). If they are different, you must find a common denominator first!',
        },
        {
          level: 2,
          title: 'Level 2: Step',
          cost: 10,
          text: expr.includes('÷') || expr.includes('/') && s.includes('divide')
            ? 'For fraction division, remember: Keep the first fraction, Change to multiplication, and Flip the divisor (reciprocal)!'
            : 'Find the Least Common Denominator (LCD). Multiply the top and bottom of each fraction by the required factor so denominators match.',
        },
        {
          level: 3,
          title: 'Level 3: Worked Solution',
          cost: 15,
          text: `Evaluate step-by-step: ${expr}. Combine the numerators over the common denominator, then simplify the final fraction to lowest terms.`,
        },
      ]
    }

    // 2. Decimals
    if (top.includes('decimal') || expr.includes('.')) {
      return [
        {
          level: 1,
          title: 'Level 1: Nudge',
          cost: 5,
          text: 'Line up your numbers strictly by their decimal points vertically. Place value is everything!',
        },
        {
          level: 2,
          title: 'Level 2: Step',
          cost: 10,
          text: 'Append trailing placeholder zeros (for example, turn 4.5 into 4.50) so every column has a digit before adding or subtracting.',
        },
        {
          level: 3,
          title: 'Level 3: Worked Solution',
          cost: 15,
          text: `Solve ${expr}: Work column-by-column starting from the rightmost place value (hundredths, tenths, ones), carrying or borrowing as needed.`,
        },
      ]
    }

    // 3. Ratios
    if (top.includes('ratio')) {
      return [
        {
          level: 1,
          title: 'Level 1: Nudge',
          cost: 5,
          text: 'Ratios scale through multiplication or division, never by adding or subtracting from both quantities.',
        },
        {
          level: 2,
          title: 'Level 2: Step',
          cost: 10,
          text: 'Find the scale factor: divide the target quantity by the starting quantity, then multiply the second quantity by that exact same factor.',
        },
        {
          level: 3,
          title: 'Level 3: Worked Solution',
          cost: 15,
          text: `Given the relationship in "${expr}": Apply the common scale factor to compute the equivalent value while preserving order.`,
        },
      ]
    }

    // 4. Geometry
    if (top.includes('geometry') || s.includes('area') || s.includes('perimeter')) {
      const isPerimeter = s.includes('perimeter')
      const isTriangle = s.includes('triangle')
      return [
        {
          level: 1,
          title: 'Level 1: Nudge',
          cost: 5,
          text: isPerimeter
            ? 'Perimeter is the total boundary distance around the outside of the shape. Do not multiply!'
            : isTriangle
            ? 'Remember: a triangle is half of a rectangle! Its area requires base × height ÷ 2.'
            : 'Area measures the flat space inside the shape in square units. Multiply length × width.',
        },
        {
          level: 2,
          title: 'Level 2: Step',
          cost: 10,
          text: isPerimeter
            ? 'Add all 4 sides together: 2 × (length + width). Make sure you do not miss any sides!'
            : isTriangle
            ? 'First multiply the base by the altitude height, then divide the result by 2.'
            : 'Identify the length and the width from the diagram, then multiply them together.',
        },
        {
          level: 3,
          title: 'Level 3: Worked Solution',
          cost: 15,
          text: `Compute ${expr}: Execute the multiplication and write your answer with square units.`,
        },
      ]
    }

    // Default
    return [
      {
        level: 1,
        title: 'Level 1: Nudge',
        cost: 5,
        text: 'Read the question carefully and determine which operation (+, −, ×, ÷) must be completed first.',
      },
      {
        level: 2,
        title: 'Level 2: Step',
        cost: 10,
        text: 'Follow the order of operations (PEMDAS): solve inside parentheses first, then multiply/divide, then add/subtract.',
      },
      {
        level: 3,
        title: 'Level 3: Worked Solution',
        cost: 15,
        text: `Calculate ${expr}: Work step-by-step and double-check your arithmetic carefully.`,
      },
    ]
  }

  return {
    parseMathVisual,
    generateHintLadder,
  }
}
