# 🚀 Quick Start Guide - BharatAce Backend

## Prerequisites ✅
- [x] Python 3.10+ installed
- [x] All packages installed
- [x] `.env` file configured
- [x] Server running on http://localhost:8000

## 5-Minute Quick Test

### Step 1: Verify Server is Running
Open your browser: http://localhost:8000

You should see:
```json
{
  "message": "BharatAce AI Campus Assistant API",
  "status": "operational",
  "version": "1.0.0"
}
```

### Step 2: Add Your First Knowledge Item

**Using the Interactive Docs:**
1. Go to http://localhost:8000/docs
2. Click on `POST /knowledge`
3. Click "Try it out"
4. Paste this JSON:
```json
{
  "content": "BharatAce University offers undergraduate programs in Computer Science, Electronics, and Mechanical Engineering. The CS program focuses on AI, Web Development, and Cloud Computing.",
  "category": "courses"
}
```
5. Click "Execute"
6. You should see a `201` response!

**Or use PowerShell:**
```powershell
$body = @{
    content = "BharatAce University offers undergraduate programs in Computer Science, Electronics, and Mechanical Engineering."
    category = "courses"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/knowledge" -Method Post -Body $body -ContentType "application/json"
```

### Step 3: Add More Knowledge

Add a few more items:

**Library Information:**
```json
{
  "content": "The university library is open from 8 AM to 10 PM on weekdays and 9 AM to 6 PM on weekends. It has over 50,000 books and provides free WiFi to all students.",
  "category": "facilities"
}
```

**Admission Information:**
```json
{
  "content": "The admission process requires 12th-grade marks (minimum 75%), entrance exam scores, and a personal interview. Applications open in May every year.",
  "category": "admission"
}
```

**Campus Life:**
```json
{
  "content": "The campus has multiple sports facilities including cricket ground, basketball courts, and a swimming pool. There are also 20+ student clubs covering tech, arts, music, and social service.",
  "category": "campus_life"
}
```

### Step 4: View All Knowledge

**Using Interactive Docs:**
1. Go to http://localhost:8000/docs
2. Click on `GET /knowledge`
3. Click "Try it out"
4. Click "Execute"

**Or use PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/knowledge" -Method Get
```

### Step 5: Ask Questions to the AI! 🤖

Now the fun part! Ask questions about your knowledge base.

**Using Interactive Docs:**
1. Go to http://localhost:8000/docs
2. Click on `POST /ask`
3. Click "Try it out"
4. Try these questions:

**Question 1:**
```json
{
  "query": "What programs does BharatAce University offer?"
}
```

**Question 2:**
```json
{
  "query": "What are the library timings?"
}
```

**Question 3:**
```json
{
  "query": "How can I apply for admission?"
}
```

**Question 4:**
```json
{
  "query": "Tell me about campus facilities"
}
```

**Or use PowerShell:**
```powershell
$question = @{
    query = "What programs does the university offer?"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Body $question -ContentType "application/json"
Write-Host $response.response
```

## 🎯 What Just Happened?

1. **You added knowledge** → Stored in Supabase database
2. **AI indexed the content** → Created embeddings for semantic search
3. **You asked questions** → AI found relevant content and generated answers
4. **You got intelligent responses** → Powered by Google Gemini!

## 🧪 Run the Automated Test Script

For a complete demo, run:
```powershell
cd backend
python test_api.py
```

This will automatically:
- Check server health ✅
- Add sample knowledge items ✅
- Retrieve all knowledge ✅
- Ask questions and show AI responses ✅

## 📊 Understanding the Flow

```
User Question
     ↓
POST /ask endpoint
     ↓
RAG Pipeline (LlamaIndex)
     ↓
1. Search knowledge base (semantic search)
2. Find relevant content
3. Send to Gemini LLM
4. Generate contextual answer
     ↓
Return AI Response
     ↓
User gets intelligent answer!
```

## 🎨 API Features You Can Try

### 1. Category-based Organization
Add knowledge with different categories:
- `courses`
- `admission`
- `facilities`
- `campus_life`
- `faculty`
- `events`

### 2. Smart Q&A
The AI can:
- Answer questions even if exact words don't match
- Combine information from multiple knowledge items
- Provide context-aware responses
- Handle follow-up questions

### 3. Easy Knowledge Management
- Add new content anytime via POST /knowledge
- View all content via GET /knowledge
- Index automatically refreshes

## 🔥 Pro Tips

1. **Be Specific**: More detailed knowledge items = better AI responses
2. **Use Categories**: Organize knowledge by topic
3. **Test Variations**: Ask the same question in different ways
4. **Add Gradually**: Start small, add more knowledge as needed
5. **Monitor Logs**: Check the server console for debugging

## 📚 Sample Knowledge Base Ideas

For a complete campus assistant, add knowledge about:
- Academic programs and courses
- Admission requirements and deadlines
- Campus facilities (library, labs, sports)
- Faculty and departments
- Scholarships and financial aid
- Student clubs and activities
- Campus rules and regulations
- Hostel information
- Placement and career services
- Events and festivals

## ⚡ Quick Commands Reference

**Start Server:**
```powershell
cd backend
python main.py
```

**Test API:**
```powershell
python test_api.py
```

**View Docs:**
Open browser: http://localhost:8000/docs

**Check Health:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

## 🎊 You're All Set!

You now have a fully functional AI-powered Campus Assistant backend!

Next: Build your frontend to create a beautiful chat interface! 💬

---

**Questions or Issues?**
- Check DEPLOYMENT_SUCCESS.md for troubleshooting
- Review README.md for detailed documentation
- Check server logs for error messages

Happy building! 🚀
