---
name: strategy-orderflow
description: >
  Order flow and market microstructure mastery for day micro-trading. Covers DOM (Depth of Market)
  reading, footprint charts, tape reading, cumulative delta, and volume profile. Use when:
  (1) analyzing real-time liquidity and order book dynamics, (2) interpreting footprint chart
  patterns, (3) reading Time & Sales tape for momentum clues, (4) identifying absorption and
  exhaustion, (5) trading POC and Value Area levels, or (6) combining order flow with price
  action for confluence entries.
---

# Order Flow & Microstructure Strategy Skill

Read the "plumbing" of price formation to identify where institutional participants are positioned and when buyer/seller aggression shifts. Order flow is the deepest layer of market analysis — it reveals what is happening *right now* in the order book, not what happened in the past.

## Core Framework: Three Tools, One Edge

| Tool | What It Shows | Time Horizon | Platform |
|------|--------------|--------------|----------|
| DOM | Live order book, liquidity walls | Real-time (100-500ms) | Tradovate, Jigsaw, Sierra Chart |
| Footprint | Bid/ask volume at each price level | Per bar (1-min, 5-min) | NinjaTrader, Sierra Chart, ATAS |
| Tape | Individual executed trades | Real-time | All platforms with T&S |

## DOM Reading Essentials

### Liquidity Walls
- Large limit orders (500+ contracts on ES, 100+ on MES) act as support/resistance.
- When price approaches a "wall" of 1,000+ contracts, expect reaction.
- If the wall gets eaten through, the move accelerates.

### Order Book Imbalance
| Imbalance | Ratio | Signal |
|-----------|-------|--------|
| Minor | 2:1 | Weak directional bias |
| Moderate | 3:1 | Tradeable directional signal |
| Significant | 5:1+ | Strong momentum expected |

### Absorption Detection
- Large market orders hit a level but price does NOT move = absorption.
- Indicates a large player absorbing selling/buying pressure.
- Often precedes reversal. **High-probability fade setup.**

### Iceberg Orders
- Level replenishes after being hit repeatedly.
- Indicates hidden institutional size.
- Do not fight the iceberg — trade WITH it once it moves.

## Footprint Chart Patterns

### 1. Imbalance Stacking
- Consecutive bid or ask imbalances at successive price levels.
- Shows aggressive buying/selling pressure.
- **Trade**: Enter in direction of imbalance, stop beyond stack.

### 2. Absorption at Key Level
- Large volume at POC, VAH, VAL, or VWAP but minimal price progress.
- Buyer/seller exhaustion at institutional benchmark.
- **Trade**: Fade the direction that just got absorbed.

### 3. Delta Divergence
- Price makes new high/low but cumulative delta does NOT confirm.
- Indicates weakening participation — trend losing fuel.
- **Trade**: Prepare reversal entry at next key level.

### 4. Exhaustion (Single Prints)
- Thin volume areas = price moves quickly through with little opposition.
- **Trade**: Expect acceleration through single prints, then stall at next volume node.

## Volume Profile Key Levels

| Level | Significance | Trading Approach |
|-------|-----------|------------------|
| POC | Most traded price = magnet | Pullback to POC = 65-70% continuation |
| VAH | Value Area High = resistance | Fade at VAH in range; break above = bullish |
| VAL | Value Area Low = support | Fade at VAL in range; break below = bearish |
| LVN | Low Volume Node = acceleration | Price moves quickly through; don't stop here |
| HVN | High Volume Node = congestion | Price stalls; targets should be beyond HVN |

## Tape Reading Quick Reference

- **Print size > 500 contracts on ES**: Institutional activity. Note the price reaction.
- **Tape accelerating in one direction with large prints**: Momentum continuation.
- **Large prints at fixed price + no movement**: Absorption = potential reversal.
- **Tape slowing as price extends**: Exhaustion = prepare exit or reversal.

## Cumulative Delta (CVD)
- Rising CVD + rising price = healthy trend.
- Falling CVD + rising price = bearish divergence = warning.
- **CVD is condition, not trigger.** Never enter solely on CVD — combine with price action.

## Reference: Order Flow Deep Research

For platform-specific tools, academic microstructure research, FIFO vs. pro-rata mechanics, and detailed pattern libraries, see `references/orderflow-deep-research.md`.
