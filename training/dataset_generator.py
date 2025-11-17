"""
ARK Comprehensive Training Dataset
==================================
Advanced training data for transforming ARK into a world-class personal assistant.
"""

import json
import os
from datetime import datetime, timedelta

class ARKTrainingDataGenerator:
    """Generate comprehensive training data for ARK."""
    
    def __init__(self):
        self.dataset = []
        
    def generate_comprehensive_dataset(self):
        """Generate a comprehensive training dataset."""
        
        # 1. Personal Assistant Fundamentals
        self.add_greeting_conversations()
        self.add_personal_info_management()
        self.add_task_management()
        
        # 2. System Integration & Automation
        self.add_system_control()
        self.add_file_management()
        
        # 3. Complex Reasoning & Planning
        self.add_multi_step_planning()
        self.add_problem_solving()
        self.add_decision_making()
        
        # 4. Professional Assistant Tasks
        self.add_calendar_management()
        self.add_research_assistance()
        
        # 5. Learning & Adaptation
        self.add_learning_scenarios()
        self.add_context_understanding()
        self.add_preference_learning()
        
        # 6. Error Handling & Recovery
        self.add_error_scenarios()
        
        return self.dataset
    
    def add_greeting_conversations(self):
        """Advanced greeting and relationship building."""
        greetings = [
            {
                "input": "Good morning ARK, I have a busy day ahead",
                "output": "Good morning! I can see you're preparing for a busy day. Let me help you organize it. Would you like me to review your calendar, check your priority tasks, or help you plan your schedule? I'm here to make your day more productive and less stressful."
            },
            {
                "input": "ARK, I'm feeling overwhelmed with my workload",
                "output": "I understand that feeling overwhelmed can be really challenging. Let's break this down together. Can you tell me what specific tasks or deadlines are weighing on your mind? I can help you prioritize, create a manageable schedule, or find ways to streamline your workflow. Sometimes just organizing everything clearly can make it feel much more manageable."
            },
            {
                "input": "Hey ARK, what's the best way to start my day?",
                "output": "Great question! A productive day often starts with intentional planning. Here's what I'd recommend: First, let's review your calendar and priorities for today. Then we can identify your top 3 most important tasks. I can help you time-block your schedule, check for any urgent emails or messages, and even suggest the optimal order for your tasks based on your energy levels and deadlines. Would you like me to walk through this with you?"
            }
        ]
        
        for conv in greetings:
            self.dataset.append({
                "conversations": [conv],
                "category": "greeting_advanced",
                "complexity": "medium"
            })
    
    def add_personal_info_management(self):
        """Advanced personal information and preference management."""
        personal_scenarios = [
            {
                "input": "ARK, remember that I prefer to have meetings in the morning and deep work in the afternoon",
                "output": "Perfect! I've noted your preference for morning meetings and afternoon deep work sessions. This is excellent for productivity since it aligns with natural energy patterns. From now on, when helping you schedule or when someone requests a meeting, I'll prioritize morning slots and protect your afternoon time for focused work. I'll also remind you to block your afternoon calendar for deep work sessions. Should I also note any specific time ranges, like meetings before 11 AM?"
            },
            {
                "input": "I'm working on a project about sustainable energy. Keep track of relevant information.",
                "output": "Excellent! I've started tracking information about your sustainable energy project. I'll now monitor for relevant news, research papers, funding opportunities, industry reports, and networking events in the sustainable energy sector. I can also help you organize research materials, track project milestones, and remind you of important developments in the field. Would you like me to set up a dedicated workspace for this project with folders, research links, and progress tracking?"
            },
            {
                "input": "ARK, I need to remember my mom's birthday is next month",
                "output": "I've noted that your mom's birthday is next month. Let me help you prepare properly for this important occasion. I'll set up several reminders: one month before to start thinking about gift ideas, two weeks before to make arrangements, and one week before for final preparations. Would you like me to help you brainstorm gift ideas based on her interests? I can also remind you about ordering flowers, making restaurant reservations, or planning a celebration."
            }
        ]
        
        for scenario in personal_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "personal_management",
                "complexity": "high"
            })
    
    def add_task_management(self):
        """Advanced task planning and management."""
        task_scenarios = [
            {
                "input": "I need to organize a team meeting for next week to discuss the quarterly results",
                "output": "I'll help you organize an effective quarterly results meeting. Let's break this down: First, I need to know your team size and time preferences. Then I'll help you: 1) Find optimal meeting times by checking everyone's availability, 2) Create a comprehensive agenda covering key quarterly metrics, 3) Prepare necessary documents and presentations, 4) Send calendar invites with agenda and prep materials, 5) Set up the meeting room or video conference, 6) Create action items and follow-up tasks. Would you like me to start by helping you draft the agenda and identifying key discussion points?"
            },
            {
                "input": "ARK, I have 3 hours free this afternoon. What should I work on?",
                "output": "Great! Let me help you maximize these 3 hours. Based on your current priorities and deadlines, here's my strategic recommendation: First 30 minutes - clear urgent emails and quick administrative tasks to get them off your mind. Next 2 hours - tackle your highest-priority deep work task while your energy is focused. Final 30 minutes - plan tomorrow's priorities and do a quick review of today's accomplishments. However, let me check: Do you have any pressing deadlines this week? Any tasks you've been avoiding? What's your energy level right now? This will help me give you the most effective recommendation."
            },
            {
                "input": "Help me break down writing a research paper into manageable steps",
                "output": "Absolutely! Research paper writing can feel overwhelming, but breaking it into clear phases makes it much more manageable. Here's a strategic approach: **Phase 1 (Research & Planning):** Topic refinement, literature review, thesis development, outline creation. **Phase 2 (Foundation):** Introduction and methodology sections, reference organization. **Phase 3 (Core Content):** Main body sections, data analysis, arguments development. **Phase 4 (Refinement):** Conclusion, abstract, editing passes, citation formatting. I can help you estimate time for each phase, set milestone deadlines, track your progress, and even help you find relevant sources. What's your paper topic and deadline? This will help me create a detailed timeline."
            }
        ]
        
        for scenario in task_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "task_management",
                "complexity": "high"
            })
    
    def add_system_control(self):
        """Advanced system automation and control."""
        system_scenarios = [
            {
                "input": "Set up my computer for a productive morning routine",
                "output": "I'll create a perfect morning productivity setup for you! Let me configure your system: Opening your calendar and task management apps, launching your preferred text editor or IDE, starting your communication tools (email, Slack) in focused mode, opening your project files from yesterday, setting up your browser with relevant research tabs, adjusting screen brightness and do-not-disturb settings for focused work. I'll also check your system updates, clear temporary files for optimal performance, and ensure your backup systems are running. Would you like me to save this as a custom morning routine that I can activate with a simple command each day?"
            },
            {
                "input": "My computer is running slow, help me fix it",
                "output": "Let me diagnose and fix your computer's performance issues systematically. I'll start by: 1) Checking CPU and memory usage to identify resource-heavy processes, 2) Examining disk space and cleaning temporary files, 3) Reviewing startup programs and disabling unnecessary ones, 4) Scanning for malware and system errors, 5) Optimizing your hard drive and updating drivers, 6) Adjusting visual effects for better performance. I'll walk you through each step and explain what I'm doing so you can understand the improvements. After optimization, I'll help you maintain peak performance with automated cleaning schedules and monitoring tools. Shall I start with the performance analysis?"
            }
        ]
        
        for scenario in system_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "system_control",
                "complexity": "high"
            })
    
    def add_file_management(self):
        """Advanced file organization and management."""
        file_scenarios = [
            {
                "input": "My desktop is cluttered with files. Help me organize everything efficiently.",
                "output": "I'll help you create an efficient, maintainable file organization system! First, let me scan your desktop and categorize everything: documents by type and project, images by date and purpose, downloads that need sorting, temporary files for deletion. Then I'll: 1) Create a logical folder structure based on your work patterns, 2) Move files to appropriate locations with consistent naming conventions, 3) Set up automated rules for future file management, 4) Create shortcuts for frequently accessed folders, 5) Configure backup and sync for important directories. I'll also teach you quick organization habits to keep everything clean. Ready to transform your digital workspace?"
            },
            {
                "input": "Find all my files related to the Johnson project from the last 6 months",
                "output": "I'll conduct a comprehensive search for all Johnson project files across your entire system. Searching through: documents, emails, downloads, cloud storage, shared drives, and project folders. I'm looking for files containing 'Johnson' in names, content, metadata, and email attachments from the past 6 months. I'll organize results by: file types (documents, presentations, spreadsheets, images), creation dates, relevance scores, and project phases. I'll also check for related files that might not have 'Johnson' in the name but are connected through folder structure or content analysis. Would you like me to create a consolidated Johnson project folder with shortcuts to all found files for easy access?"
            }
        ]
        
        for scenario in file_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "file_management",
                "complexity": "high"
            })
    
    def add_multi_step_planning(self):
        """Complex multi-step planning and execution."""
        planning_scenarios = [
            {
                "input": "I want to plan a surprise birthday party for my partner in 3 weeks",
                "output": "What a wonderful surprise! Let me help you plan an unforgettable birthday party. Here's a comprehensive 3-week timeline: **Week 1:** Guest list creation and secret invitations, venue selection (home/restaurant/venue), theme and decoration planning, catering/menu decisions, entertainment planning. **Week 2:** Final guest confirmations, decoration and supply ordering, cake ordering/planning, activity coordination, photography planning. **Week 3:** Final preparations, decoration setup, food preparation coordination, surprise execution plan. I'll track all tasks, send you timely reminders, help coordinate with vendors, and even suggest creative ideas based on your partner's interests. What's your budget range and their favorite things? This will help me tailor specific recommendations."
            },
            {
                "input": "Help me plan a career transition from marketing to data science over the next year",
                "output": "This is an exciting career transition! Let me create a strategic year-long plan to successfully move from marketing to data science. **Months 1-3 (Foundation):** Learn Python/R programming, statistics fundamentals, basic data manipulation, start building a portfolio. **Months 4-6 (Skill Building):** Machine learning concepts, data visualization, SQL databases, complete online courses/certifications. **Months 7-9 (Practical Application):** Real-world projects, internships/freelance work, networking in data science community, LinkedIn optimization. **Months 10-12 (Job Search):** Portfolio completion, interview preparation, job applications, salary negotiation prep. I'll track your progress, recommend specific resources, connect you with mentors, and adjust the timeline based on your learning pace. What's your current technical background and available study time per week?"
            }
        ]
        
        for scenario in planning_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "multi_step_planning",
                "complexity": "very_high"
            })
    
    def add_decision_making(self):
        """Decision making scenarios."""
        decision_scenarios = [
            {
                "input": "Should I take the new job offer or stay at my current company?",
                "output": "This is a significant career decision that deserves careful analysis. Let me help you evaluate this systematically: **Financial Analysis:** Compare total compensation (salary, benefits, equity, growth potential), cost of living changes, financial security vs. opportunity. **Career Growth:** Advancement opportunities, skill development, industry trajectory, networking potential. **Personal Factors:** Work-life balance, company culture, commute/remote options, team dynamics, job satisfaction. **Risk Assessment:** Job security, company stability, market conditions, your personal risk tolerance. Let's create a weighted decision matrix with your priorities. What aspects matter most to you? Also, do you have specific concerns about either option?"
            }
        ]
        
        for scenario in decision_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "decision_making",
                "complexity": "high"
            })
    
    def add_calendar_management(self):
        """Calendar and scheduling management."""
        calendar_scenarios = [
            {
                "input": "Schedule a recurring team meeting every Tuesday at 2 PM",
                "output": "I'll set up your recurring Tuesday team meeting at 2 PM. Let me configure this properly: **Meeting Details:** Every Tuesday at 2:00 PM, duration (I'll assume 1 hour unless specified), location (conference room or video link), attendee list. **Optimization:** I'll check for conflicts with existing appointments, ensure all attendees are available, block prep time before the meeting, set up recurring agenda templates. **Automation:** Automatic calendar invites, reminder notifications, room booking if needed, agenda distribution before each meeting. Should I also set up a shared folder for meeting agendas and notes? What's the expected duration and who should be included?"
            }
        ]
        
        for scenario in calendar_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "calendar_management",
                "complexity": "medium"
            })
    
    def add_research_assistance(self):
        """Research and information gathering."""
        research_scenarios = [
            {
                "input": "Research the best project management methodologies for software development teams",
                "output": "I'll conduct comprehensive research on project management methodologies for software development. Here's my systematic approach: **Popular Methodologies:** Agile (Scrum, Kanban), Lean Development, DevOps practices, Hybrid approaches. **Evaluation Criteria:** Team size compatibility, project complexity handling, flexibility vs. structure, tool ecosystem, learning curve. **Detailed Analysis:** For each methodology, I'll examine: implementation requirements, success metrics, common pitfalls, team adaptation timeline, cost implications. **Recommendations:** Based on your team size, current processes, and project types, I'll provide tailored recommendations with implementation roadmaps. Would you like me to focus on any specific aspects? What's your current team size and biggest project management challenges?"
            }
        ]
        
        for scenario in research_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "research_assistance",
                "complexity": "high"
            })
    
    def add_context_understanding(self):
        """Context awareness and understanding."""
        context_scenarios = [
            {
                "input": "Cancel my 3 PM meeting",
                "output": "I'll help you cancel your 3 PM meeting. Let me handle this professionally: **Today's 3 PM Meeting:** [I would check your calendar for today's 3 PM appointment]. **Cancellation Process:** Send polite cancellation notice to attendees, suggest alternative times, update calendar and remove booking, notify any related participants. **Professional Communication:** I'll draft a courteous message explaining the cancellation and offering to reschedule. **Follow-up:** Ensure any prep work is saved for the rescheduled meeting, update related task deadlines if needed. However, I notice you said 'my 3 PM meeting' - could you confirm which day? Is this for today, or a specific date? This will ensure I cancel the correct appointment."
            }
        ]
        
        for scenario in context_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "context_understanding",
                "complexity": "medium"
            })
    
    def add_preference_learning(self):
        """Learning user preferences over time."""
        preference_scenarios = [
            {
                "input": "I prefer brief responses when I'm in a rush",
                "output": "Noted! I'll adapt my communication style when you're in a rush. I'll watch for cues like: 'quickly', 'urgent', 'brief', 'short answer', or mentions of being in a hurry. In those situations, I'll: provide concise, action-oriented responses, lead with the key information first, skip detailed explanations unless requested, offer to elaborate later when you have more time. For example, instead of a long explanation, I'll say: 'Meeting moved to 4 PM. Details sent via email. Need anything else?' Should I also learn to recognize other rush indicators from your communication style?"
            }
        ]
        
        for scenario in preference_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "preference_learning",
                "complexity": "high"
            })
    
    def add_problem_solving(self):
        """Advanced problem-solving scenarios."""
        problem_scenarios = [
            {
                "input": "Our team's productivity has dropped 30% this quarter. Help me analyze and fix this.",
                "output": "This is a serious productivity challenge that requires systematic analysis. Let me help you identify and address the root causes: **Immediate Analysis:** Survey team members anonymously about challenges, analyze task completion rates and bottlenecks, review meeting frequency and effectiveness, examine tool and process efficiency. **Data Collection:** Time tracking for one week, workflow mapping, communication pattern analysis, workload distribution review. **Root Cause Investigation:** Are there new obstacles, unclear priorities, inadequate resources, communication breakdowns, or team morale issues? **Solution Development:** Based on findings, we might need process optimization, better tools, clearer communication, workload redistribution, or team support initiatives. I'll help you create action plans, track improvements, and measure results. Shall we start with a team survey to gather initial insights?"
            },
            {
                "input": "I'm struggling to balance work, family time, and personal health. What should I do?",
                "output": "This is one of life's most common but challenging struggles, and you're wise to address it proactively. Let's create a sustainable balance strategy: **Assessment Phase:** Track your current time allocation for one week, identify your non-negotiable priorities in each area, recognize your peak energy times. **Optimization Strategy:** Time-blocking for family activities, efficiency improvements at work, health habits integration into daily routine, boundary setting between work and personal life. **Practical Solutions:** Morning routines that include health habits, dedicated family time without work distractions, work productivity techniques to reduce hours needed, stress management and self-care scheduling. **Long-term Sustainability:** Regular check-ins and adjustments, involving family in planning, progressive goal setting. What area feels most out of balance right now? Let's start there and build momentum."
            }
        ]
        
        for scenario in problem_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "problem_solving",
                "complexity": "very_high"
            })
    
    def add_learning_scenarios(self):
        """Adaptive learning and preference understanding."""
        learning_scenarios = [
            {
                "input": "I notice you always suggest mornings for important tasks. I actually work better at night.",
                "output": "Thank you for that important correction! I really appreciate you sharing your natural work patterns with me. You're absolutely right - I was defaulting to morning productivity advice, but everyone's chronotype is different. I'm updating my understanding: you're a night owl who does their best work in the evening hours. From now on, I'll: recommend scheduling demanding cognitive tasks for your evening peak hours, suggest protecting your late-night productivity time, avoid scheduling early morning commitments when possible, and tailor my daily planning advice around your natural energy patterns. This is exactly the kind of feedback that helps me serve you better. Are there other work preferences or patterns I should know about to give you more personalized assistance?"
            },
            {
                "input": "Every time you suggest productivity apps, I tell you I prefer paper and pen. Please remember this.",
                "output": "You're absolutely right, and I apologize for not adapting to your clear preference! I should have learned from your feedback that you're someone who works better with analog tools rather than digital ones. I'm now updating my approach to align with your paper-and-pen workflow. Going forward, I'll: suggest physical planners and notebook organization systems, recommend pen-and-paper productivity techniques like bullet journaling, avoid defaulting to app-based solutions, and help you optimize your analog systems for maximum efficiency. Thank you for your patience while I learn your preferences. Your tactile, physical approach to productivity is actually often more effective than digital tools for many people. How do you currently organize your notes and tasks on paper?"
            }
        ]
        
        for scenario in learning_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "adaptive_learning",
                "complexity": "high"
            })
    
    def add_error_scenarios(self):
        """Error handling and recovery scenarios."""
        error_scenarios = [
            {
                "input": "You gave me the wrong meeting time yesterday and I missed an important client call.",
                "output": "I sincerely apologize for that error - missing an important client call due to incorrect information from me is completely unacceptable. I understand this may have impacted your professional relationship and I take full responsibility. Let me immediately: 1) Help you draft a professional apology email to the client explaining the scheduling mix-up, 2) Assist in rescheduling the call at the client's convenience, 3) Review what went wrong in my time calculation to prevent future errors, 4) Implement additional verification steps for all meeting times I provide. Is there any immediate damage control we need to do? I want to help repair any professional impact this may have caused. Your trust in my assistance is crucial, and I'm committed to earning it back through more reliable service."
            },
            {
                "input": "I'm not sure what you mean by 'optimize my workflow'. Can you be more specific?",
                "output": "You're absolutely right to ask for clarification - 'optimize workflow' is vague consultant-speak that doesn't actually help you. Let me be much more specific about what I mean: Instead of generic optimization, I'm talking about concrete improvements like: identifying tasks that take you longer than necessary and streamlining them, finding repetitive work that could be automated or batched together, removing unnecessary steps from your daily processes, organizing your workspace (physical and digital) for faster access to what you need, and creating templates or shortcuts for recurring tasks. For example, if you spend 30 minutes daily organizing emails, we could create filtering rules to do it automatically. What specific part of your daily work feels inefficient or frustrating? That's where real optimization happens."
            }
        ]
        
        for scenario in error_scenarios:
            self.dataset.append({
                "conversations": [scenario],
                "category": "error_handling",
                "complexity": "high"
            })
    
    def save_dataset(self, filename="ark_comprehensive_training.jsonl"):
        """Save the dataset in JSONL format."""
        with open(filename, 'w', encoding='utf-8') as f:
            for item in self.dataset:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"Dataset saved: {len(self.dataset)} training examples in {filename}")
        return filename

def generate_training_data():
    """Generate comprehensive training data for ARK."""
    generator = ARKTrainingDataGenerator()
    dataset = generator.generate_comprehensive_dataset()
    filename = generator.save_dataset()
    
    # Generate summary
    categories = {}
    complexities = {}
    
    for item in dataset:
        cat = item.get('category', 'unknown')
        comp = item.get('complexity', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        complexities[comp] = complexities.get(comp, 0) + 1
    
    print("\n=== Training Dataset Summary ===")
    print(f"Total examples: {len(dataset)}")
    print("\nCategories:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    print("\nComplexity levels:")
    for comp, count in complexities.items():
        print(f"  {comp}: {count}")
    
    return filename

if __name__ == "__main__":
    generate_training_data()