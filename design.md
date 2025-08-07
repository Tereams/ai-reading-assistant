# design.md

This document provides reflections on the design decisions, implementation trade-offs, and future improvements for the **AI Reading Assistant** agent.


## 1. Problem Framing: Why This Problem? What Does Success Look Like?

As someone with a strong interest in reading, I often find myself starting many books but failing to finish them. I wanted to address this recurring personal issue — lack of reading consistency — by building a system that keeps me accountable and engaged.

In addition, from my reading in *Psychology (12th ed, David G. Myers, 2022)*, I learned that asking questions is one of the most effective ways to reinforce learning. That inspired me to leverage LLMs to generate reflective questions and evaluate my answers — turning passive reading into an active learning process.

**Success**, to me, looks like this:

- Each morning, the user receives a concise summary and two thoughtful questions about the day’s reading.
- In the evening, they are prompted to reflect and write answers, which are then evaluated by the AI.

## 2. Libraries / APIs / Frameworks Used and Why

| Tool                         | Purpose         | Why                                                  |
| ---------------------------- | --------------- | ---------------------------------------------------- |
| **Streamlit**                | Frontend UI     | Rapid prototyping; easy to deploy and test           |
| **PyMuPDF**                  | PDF parsing     | Accurate, lightweight, and supports cover extraction |
| **OpenRouter + GLM-4.5-Air** | LLM backend     | Free-tier model with good quality output             |
| **APScheduler**              | Task scheduling | Flexible and reliable for timed triggers             |
| **Yagmail**                  | Email sending   | Simple Gmail integration for reminders               |

I prioritized speed of iteration over robustness for this take-home assignment, choosing tools that let me quickly express my ideas through a working prototype.


## 3. Prompt Engineering and Output Evaluation

The system uses **three main prompts**:

1. **Question generation prompt**  
   
   - Strict format: exactly two numbered questions  
   - Post-processed using regular expressions  
   - Includes a retry loop if formatting fails

2. **Summary generation prompt**  
   
   - Instructs the LLM to produce a concise, 3-sentence summary with no extra formatting

3. **Answer evaluation prompt**  
   
   - Combines the user’s answers, the summary, and the original questions  
   - Evaluates response quality, engagement, and gives a recommendation:
     - `"Advance"` if the reflection is strong
     - `"Review Again"` if the engagement is lacking

This structured prompt design ensures clarity, consistency, and control over LLM behavior — even when using a free-tier model.


## 4. How Does the Agent Know When Its Task Is Complete?

The agent determines completion when it has:

- Generated a summary and questions for the day
- Sent the morning reading email
- Sent the evening summary reminder
- Logged the day’s data (including LLM feedback and answers)

I did not implement a full “meta-loop” for the agent to decide when to stop — because in this particular use case, persistent daily operation is the expected behavior. That said, adding a “self-termination logic” would be an interesting future improvement.


## 5. Failure Modes Considered and Mitigated

I took care to anticipate and mitigate several potential failure cases:

- **LLM instability / bad output**
  
  - Added retry logic (up to 5 times) when generating prompts
  - Output post-processed and validated for correctness

- **Uninitialized or missing files**
  
  - Defaults loaded for user/profile/notes files if missing

- **Silent failures**
  
  - Logging is included at all key steps to trace execution path

Though simple, these safety mechanisms ensure the system can run unattended.

## 6. What Would You Improve with Another Week?

With more time, I would make the system more **intelligent, scalable, and user-friendly**:

### Agent Autonomy

- Let the agent determine how many days are needed to read a book, based on a target pace (e.g., “fast” vs. “slow”)
- The agent decides whether they are ready to proceed or need to review — creating a self-contained loop of learning and reflection.
- Let the agent select books based on user interests — possibly even scrape and parse them automatically

### Multi-user Support

- Add user authentication and login system
- Move from file-based storage to a relational or document-based database (e.g., PostgreSQL, MongoDB)

### UI Enhancements

- Migrate from Streamlit to a modern frontend (e.g., React + FastAPI)
- Improve visual design and usability of the reading interface


## Final Notes

This project reflects my belief in AI as a tool not just for automation, but for meaningful human growth — in this case, forming a consistent, reflective reading habit. I hope it demonstrates my ability to combine engineering, product thinking, and creativity to build impactful tools.
