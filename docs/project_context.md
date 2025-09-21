# Project Context and Aim

## What I Am Doing
This B.Tech project is inspired by *Automated Planning and Acting* by Malik Ghallab, Dana Nau, and Paolo Traverso.  
I have carefully read **Chapter 2** of the book, which introduces planning with deterministic models and explains how to represent states, actions, and goals. The toy world described in **Example 2.3** forms the core problem I am working on.

My aim is to **understand the planning problem deeply and then simulate it in Python** using modern planning libraries.

## Why Example 2.3?
- It provides a **well-structured logistics/piles domain**: robots, docks, containers, and piles.  
- The problem is simple enough to simulate, yet rich enough to explore different planning concepts: state-variable models, action preconditions/effects, and goals.  
- It serves as a foundation to test **search algorithms (UCS, A*, GBFS, etc.)** and **heuristics (h_add, h_max, h_ff, landmarks, etc.)**.

## Steps of My Project
1. **Theory Study** – Summarized in [`ch2_summary.md`](ch2_summary.md).  
   - Covers the modeling, search algorithms, heuristics, and optimizations presented in Chapter 2.  
2. **Practical Simulation** – Explained in [`guide_up.md`](guide_up.md).  
   - Encodes Example 2.3 in the **Unified Planning** library, defines the fluents and actions, sets the initial state, and solves for plans.  
3. **Context & Aim** – This file (`project_context.md`) explains **why** I am doing the project and provides a roadmap.

## My Aim
- **Simulate Example 2.3 in Python** using the Unified Planning library.  
- **Experiment with planning algorithms and heuristics** (GBFS, A*, h_ff, etc.).  
- **Gradually increase the complexity**: start with one robot and one container, then extend to multiple robots, piles, and more complex goals.  
- **Analyze and compare performance** of search strategies and heuristics as the problem scales.  

Ultimately, this project will strengthen my understanding of **AI planning** and give me hands-on experience with modern planning toolkits while connecting theory to practice.
