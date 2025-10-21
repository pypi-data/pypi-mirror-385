#!/usr/bin/env python3
"""
Classwork Generation Example for the Henotace AI Python SDK
Demonstrates how to generate practice questions based on conversation history
"""

import asyncio
import os
import sys
import json
sys.path.append('..')
sys.path.append('../src')
from henotace_ai import HenotaceAI, create_tutor, SessionSubject, InMemoryConnector


async def main():
    # Get API key from environment variable
    api_key = os.getenv('HENOTACE_API_KEY')
    if not api_key:
        print("❌ Please set HENOTACE_API_KEY environment variable")
        print("   Example: export HENOTACE_API_KEY=your_api_key_here")
        return
    
    print("🚀 Henotace AI Python SDK - Classwork Generation Demo")
    print("=" * 60)
    
    # Initialize the SDK with storage
    print("📡 Initializing SDK with storage...")
    sdk = HenotaceAI(
        api_key=api_key,
        storage=InMemoryConnector()  # For session persistence
    )
    
    # Check API status
    print("🔍 Checking API status...")
    try:
        if sdk.get_status_ok():
            print("✅ API is available and ready!")
        else:
            print("❌ API is not available")
            return
    except Exception as e:
        print(f"❌ Error checking API status: {e}")
        return
    
    # Create a math tutor
    print("\n👨‍🏫 Creating Math Tutor...")
    tutor = await create_tutor(
        sdk=sdk,
        student_id="demo_student_001",
        tutor_name="Math Tutor",
        subject=SessionSubject(
            id="mathematics",
            name="Mathematics",
            topic="Algebra"
        ),
        grade_level="high_school",
        language="en"
    )
    
    print(f"✅ Created tutor: {tutor.tutor_id}")
    
    # Set up the tutor with persona and context
    print("\n🎭 Setting up tutor persona...")
    tutor.set_persona(
        "You are an enthusiastic math tutor who specializes in algebra. "
        "You explain concepts clearly, use step-by-step examples, and "
        "encourage students to understand the reasoning behind solutions."
    )
    
    tutor.set_context([
        "The student is learning algebra for the first time.",
        "They prefer step-by-step explanations with examples.",
        "Focus on building understanding, not just giving answers."
    ])
    
    # Simulate a tutoring session
    print("\n💬 Simulating a tutoring session...")
    print("-" * 40)
    
    # Conversation about solving linear equations
    conversation = [
        "Can you help me understand how to solve linear equations?",
        "What's the difference between 2x + 5 = 13 and 2x - 5 = 13?",
        "How do I check if my answer is correct?",
        "Can you show me how to solve equations with fractions?",
        "What about equations with variables on both sides?"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n👤 Student: {message}")
        response = await tutor.send(message)
        print(f"🤖 Tutor: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    # Show conversation history
    history = tutor.history()
    print(f"\n📜 Conversation completed! Total messages: {len(history)}")
    
    # Generate classwork based on the conversation
    print("\n📝 Generating classwork questions...")
    print("-" * 40)
    
    try:
        # Generate easy questions
        print("\n🟢 Generating EASY difficulty questions...")
        easy_classwork = await tutor.generate_classwork(
            question_count=3,
            difficulty='easy'
        )
        
        print(f"✅ Generated {len(easy_classwork.get('questions', []))} easy questions")
        print_classwork(easy_classwork, "EASY")
        
        # Generate medium questions
        print("\n🟡 Generating MEDIUM difficulty questions...")
        medium_classwork = await tutor.generate_classwork(
            question_count=4,
            difficulty='medium'
        )
        
        print(f"✅ Generated {len(medium_classwork.get('questions', []))} medium questions")
        print_classwork(medium_classwork, "MEDIUM")
        
        # Generate hard questions
        print("\n🔴 Generating HARD difficulty questions...")
        hard_classwork = await tutor.generate_classwork(
            question_count=3,
            difficulty='hard'
        )
        
        print(f"✅ Generated {len(hard_classwork.get('questions', []))} hard questions")
        print_classwork(hard_classwork, "HARD")
        
        # Save classwork to file
        all_classwork = {
            'easy': easy_classwork,
            'medium': medium_classwork,
            'hard': hard_classwork,
            'metadata': {
                'subject': 'Mathematics',
                'topic': 'Algebra',
                'student_id': tutor.student_id,
                'tutor_id': tutor.tutor_id,
                'total_questions': len(easy_classwork.get('questions', [])) + 
                                 len(medium_classwork.get('questions', [])) + 
                                 len(hard_classwork.get('questions', []))
            }
        }
        
        with open('generated_classwork.json', 'w') as f:
            json.dump(all_classwork, f, indent=2)
        
        print(f"\n💾 Classwork saved to 'generated_classwork.json'")
        print(f"📊 Total questions generated: {all_classwork['metadata']['total_questions']}")
        
    except Exception as e:
        print(f"❌ Error generating classwork: {e}")
        return
    
    print("\n🎉 Classwork generation demo completed successfully!")
    print("=" * 60)


def print_classwork(classwork, difficulty_level):
    """Print classwork questions in a formatted way"""
    questions = classwork.get('questions', [])
    metadata = classwork.get('metadata', {})
    
    print(f"\n📋 {difficulty_level} DIFFICULTY QUESTIONS:")
    print(f"   Subject: {metadata.get('subject', 'N/A')}")
    print(f"   Topic: {metadata.get('topic', 'N/A')}")
    print(f"   Count: {len(questions)}")
    
    for i, question in enumerate(questions, 1):
        print(f"\n   {i}. {question.get('question', 'No question text')}")
        
        # Show options if it's a multiple choice question
        if question.get('type') == 'multiple_choice' and question.get('options'):
            for j, option in enumerate(question['options'], 1):
                print(f"      {chr(64+j)}. {option}")
        
        # Show correct answer if available
        if question.get('correct_answer'):
            print(f"      ✅ Answer: {question['correct_answer']}")
        
        # Show explanation if available
        if question.get('explanation'):
            print(f"      💡 Explanation: {question['explanation']}")


async def interactive_demo():
    """Interactive demo where user can chat and generate classwork"""
    api_key = os.getenv('HENOTACE_API_KEY')
    if not api_key:
        print("❌ Please set HENOTACE_API_KEY environment variable")
        return
    
    print("🚀 Interactive Classwork Generation Demo")
    print("=" * 50)
    print("Chat with the tutor, then generate classwork based on your conversation!")
    print("Type 'generate' to create classwork, 'quit' to exit")
    print("-" * 50)
    
    sdk = HenotaceAI(api_key=api_key, storage=InMemoryConnector())
    
    if not sdk.get_status_ok():
        print("❌ API is not available")
        return
    
    # Create tutor
    tutor = await create_tutor(
        sdk=sdk,
        student_id="interactive_student",
        tutor_name="Interactive Tutor",
        subject=SessionSubject(id="general", name="General", topic="Mixed Topics")
    )
    
    tutor.set_persona("You are a helpful tutor who adapts to any subject. Be engaging and educational.")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'generate':
                if len(tutor.history()) < 2:
                    print("❌ Need at least 2 messages to generate classwork")
                    continue
                
                print("\n📝 Generating classwork...")
                try:
                    classwork = await tutor.generate_classwork(question_count=5, difficulty='medium')
                    print_classwork(classwork, "GENERATED")
                except Exception as e:
                    print(f"❌ Error: {e}")
                continue
            
            if not user_input:
                continue
            
            print("🤖 Tutor: ", end="", flush=True)
            response = await tutor.send(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Henotace AI Classwork Generation Demo')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run interactive demo instead of automated demo')
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_demo())
    else:
        asyncio.run(main())
