# Prompt Assistant - User Guide

> **📌 Updated for v3.6.7-beta**: The AI Assistant has been renamed to "Prompt Assistant" and moved to the Prompt Library as a third tab for better organization and workflow. Enhanced with clickable folder links and improved UI clarity.

## 🎯 Quick Start Guide

The Prompt Assistant helps you improve your translation prompts using natural language conversation with AI. No need to manually edit complex prompt text - just describe what you want to change!

---

## 📖 How to Use

### **Step 1: Open Prompt Library**

1. Open Supervertaler
2. Go to **Menu → Prompt Library → Open Prompt Library** (or press **Ctrl+P**)
3. The Prompt Library window appears

### **Step 2: Navigate to Prompt Assistant Tab**

1. Click on the **"🤖 Prompt Assistant"** tab (third tab after System Prompts and Custom Instructions)
2. The editor panel hides automatically for full-width workspace
3. You'll see the conversational interface for prompt refinement

### **Step 3: Select a Prompt to Improve**

1. First, select a prompt from the **System Prompts** or **Custom Instructions** tabs
2. Switch back to the **Prompt Assistant** tab
3. The selected prompt is ready for AI-powered improvements

### **Step 4: Request Modifications**

Type your request in natural language. For example:

**Simple Requests:**
- "Make it more formal"
- "Add emphasis on terminology consistency"
- "Simplify the language"
- "Make it friendlier"

**Specific Requests:**
- "Add a note about preserving brand names"
- "Include instructions for handling technical abbreviations"
- "Emphasize cultural sensitivity"
- "Add guidance for handling numbers and dates"

**Complex Requests:**
- "Make it more suitable for legal documents"
- "Add specific instructions for medical terminology"
- "Emphasize literal accuracy over fluency"
- "Include examples of preferred translations"

### **Step 4: Request Modifications**

Type your request in the chat input. The AI will understand requests like:
- "Make it more formal"
- "Add emphasis on terminology consistency"
- "Include instructions for handling technical abbreviations"

### **Step 5: Review Changes**

1. Click **"📤 Send Request"** (or press Enter)
2. Wait a few seconds for AI to process
3. Review the proposed changes in the diff panel
   - **Green lines** = additions
   - **Red lines** = deletions
4. Read the AI's explanation in the chat

### **Step 6: Apply or Refine**

**Option A: Apply Changes**
- If you like the changes, click **"✅ Apply Changes"**
- The prompt is updated immediately
- Success message appears

**Option B: Refine Further**
- If you want more changes, continue chatting
- Type another request like "Also add more emphasis on context"
- The AI will build on the previous version

**Option C: Discard**
- If you don't like the changes, click **"❌ Discard Changes"**
- The original prompt remains unchanged
- Start over with a new request

---

## 💡 Tips & Best Practices

### **Writing Good Requests**

✅ **Be Specific:**
- "Add emphasis on cultural context" ✓
- "Make it better" ✗

✅ **Focus on One Change at a Time:**
- Good: "Make the tone more formal"
- Better: "Make the tone more formal" → then → "Add emphasis on terminology"

✅ **Use Translation-Specific Terms:**
- "formal tone"
- "literal translation"
- "cultural adaptation"
- "terminology consistency"
- "preserve formatting"

### **Example Conversations**

**Example 1: Making a Prompt More Professional**
```
You: Make this more professional and formal

AI: I've suggested modifications to increase formality...
[Shows diff]

You: Perfect! Also add emphasis on industry-specific terminology

AI: I've added guidance for terminology handling...
[Shows updated diff]

[Click Apply Changes]
```

**Example 2: Domain-Specific Adjustments**
```
You: This prompt is for legal documents. Add appropriate guidelines.

AI: I've added legal-specific instructions including...
[Shows diff]

You: Good, but also mention maintaining original sentence structure

AI: I've added a note about sentence structure preservation...
[Shows updated diff]

[Click Apply Changes]
```

---

## 🎨 Understanding the Interface

### **Prompt Assistant Tab Interface**

```
[10:23:45] You: Make it more formal
[10:23:48] Prompt Assistant: ✅ I've suggested modifications...
```

- **Blue** = Your messages
- **Green** = AI responses
- **Red** = Error messages
- **Gray** = Timestamps

**Full-Width Workspace**: The editor panel automatically hides when you're on the Prompt Assistant tab, giving you maximum space for the conversation and diff view.

### **Diff Panel (Right Side)**

```
--- Original Prompt
+++ Modified Prompt

  You are a professional translator.
- Your goal is to translate accurately.
+ Your primary objective is to produce precise, 
+ contextually appropriate translations.
```

- **Lines without +/-** = Unchanged
- **Lines with +** (green) = Added
- **Lines with -** (red) = Removed

---

## ⚙️ Advanced Features

### **Iterative Refinement**

You can have a conversation with the AI to refine your prompt through multiple iterations:

1. Make initial request → Review → Apply
2. Make another request → Review → Apply
3. Continue until perfect!

The AI remembers the context of your conversation, so you can build on previous changes.

### **Keyboard Shortcuts**

- **Enter** = Send request
- **Shift+Enter** = New line in input box
- **Ctrl+P** = Open Prompt Library (from main window)

---

## 🔧 Troubleshooting

### **"No prompt selected" warning**
**Solution:** Click on a prompt in the list first, then make your request.

### **"Failed to get AI suggestion" error**
**Possible causes:**
- No API key configured
- Network connection issue
- Invalid API key

**Solution:**
1. Check your API keys (Menu → Settings → API Keys)
2. Verify internet connection
3. Try a different LLM provider

### **AI suggestion doesn't match my request**
**Solution:**
- Be more specific in your request
- Try rephrasing
- Break complex requests into smaller steps

### **Changes don't appear after clicking Apply**
**Solution:**
- Refresh the Prompt Library (click 🔄 Refresh button)
- Close and reopen the Prompt Library
- Check the file was saved (look for success message)

---

## 📊 Example Use Cases

### **Use Case 1: Adapting a General Prompt for Technical Translation**

**Original Prompt:**
> "You are a professional translator. Translate accurately while maintaining natural flow."

**User Request:**
> "Make this suitable for technical documentation with lots of specialized terminology"

**Result:**
> "You are a professional technical translator specializing in software documentation. Prioritize terminology consistency and technical accuracy over stylistic fluency. Maintain all technical terms, code snippets, and product names exactly as they appear. When in doubt, favor literal translation over creative adaptation."

### **Use Case 2: Adding Cultural Context Awareness**

**Original Prompt:**
> "Translate the following text from English to Spanish."

**User Request:**
> "Add emphasis on cultural adaptation and localization for Latin American audience"

**Result:**
> "Translate the following text from English to Spanish (Latin American variant). Pay special attention to cultural context and local idioms. Adapt metaphors and cultural references appropriately. Consider regional variations in vocabulary and avoid Peninsular Spanish constructions that might sound formal or outdated in Latin America."

### **Use Case 3: Quality-Focused Translation**

**Original Prompt:**
> "Translate this text carefully."

**User Request:**
> "Transform this into a comprehensive prompt emphasizing quality assurance and accuracy"

**Result:**
> "You are an expert translator with a focus on quality assurance. For this translation:
> 
> 1. Read the entire source text before beginning
> 2. Verify terminology consistency throughout
> 3. Check for ambiguities and contextual clues
> 4. Maintain formatting and structure
> 5. Review your translation for accuracy
> 6. Flag any unclear passages or potential issues
> 
> Prioritize accuracy and completeness over speed."

---

## 🎓 Learning Resources

### **Understanding Prompt Engineering**

Good prompts tell the AI:
- **WHO** it is (role/expertise)
- **WHAT** to do (task)
- **HOW** to do it (style, approach, constraints)
- **WHAT NOT** to do (avoid, limitations)

### **Prompt Components**

1. **Role Definition:** "You are a professional legal translator..."
2. **Task Description:** "Translate the following contract..."
3. **Quality Guidelines:** "Maintain formal register..."
4. **Constraints:** "Do not translate proper names..."
5. **Examples:** "For example, translate 'hereinafter' as..."

---

## 🚀 Pro Tips

### **1. Start Broad, Then Refine**

First request: "Make this more professional"  
Second request: "Add legal terminology guidelines"  
Third request: "Include example translations for common terms"

### **2. Use Industry Terminology**

Instead of: "Make it sound better"  
Try: "Increase formality and use professional register"

### **3. Think About Your Audience**

Consider mentioning:
- Target audience (general public, experts, etc.)
- Formality level needed
- Regional variations
- Industry standards

### **4. Learn from Good Prompts**

Browse the pre-built prompts in the library to see what works well, then ask the AI to adapt them for your specific needs.

---

## 📞 Need Help?

If you have questions or suggestions:
- **GitHub Issues:** Report bugs or request features
- **User Forum:** Share tips and ask questions
- **Email Support:** michael@supervertaler.com

---

## 🎉 Happy Translating!

The AI Prompt Assistant makes prompt engineering accessible to everyone. No technical knowledge needed - just describe what you want in plain language!

**Remember:** Good prompts = Better translations = Happier clients ✨
