import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import PyPDF2
import docx
import io
import base64
from typing import List, Dict, Any
import json
import requests
import time

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="O3-Pro Azure Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AzureO3ProClient:
    """Client for Azure OpenAI O3-Pro model"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
        self.model = os.getenv("AZURE_OPENAI_MODEL")
        
        # Build the complete URL for O3-Pro responses endpoint
        if self.endpoint and not self.endpoint.endswith('/'):
            self.endpoint = self.endpoint + '/'
        
        self.api_url = f"{self.endpoint}openai/responses?api-version={self.api_version}"
    
    def create_chat_completion(self, messages: List[Dict], stream: bool = False):
        """Create chat completion using Azure OpenAI O3-Pro responses endpoint"""
        try:
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            # Convert messages to O3-Pro input format
            input_text = self._convert_messages_to_input(messages)
            
            # O3-Pro specific payload format
            payload = {
                "model": self.model,
                "input": input_text,
                "stream": stream
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                stream=stream,
                timeout=60
            )
            
            if response.status_code == 200:
                if stream:
                    return self._handle_streaming_response(response)
                else:
                    return response.json()
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error calling Azure OpenAI: {str(e)}")
            return None
    
    def _convert_messages_to_input(self, messages: List[Dict]) -> str:
        """Convert chat messages to O3-Pro input format"""
        input_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                input_parts.append(f"System: {content}")
            elif role == "user":
                input_parts.append(f"User: {content}")
            elif role == "assistant":
                input_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(input_parts)
    
    def _handle_streaming_response(self, response):
        """Handle streaming response from O3-Pro"""
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data != '[DONE]':
                            try:
                                chunk = json.loads(data)
                                yield chunk
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            st.error(f"Error processing streaming response: {str(e)}")
    
    def _extract_content_from_o3_response(self, response_data):
        """Extract content from O3-Pro response format"""
        try:
            if 'output' in response_data:
                for output_item in response_data['output']:
                    if output_item.get('type') == 'message' and 'content' in output_item:
                        for content_item in output_item['content']:
                            if content_item.get('type') == 'output_text':
                                return content_item.get('text', '')
            return None
        except Exception as e:
            st.error(f"Error extracting content from response: {str(e)}")
            return None

def extract_text_from_pdf(file) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_docx(file) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file) -> str:
    """Extract text from TXT file"""
    try:
        return str(file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error reading TXT: {str(e)}")
        return ""

def process_uploaded_file(uploaded_file) -> str:
    """Process uploaded file and extract text"""
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif file_type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    else:
        st.warning(f"Unsupported file type: {file_type}")
        return ""

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful AI assistant powered by O3-Pro."
    if "uploaded_files_content" not in st.session_state:
        st.session_state.uploaded_files_content = {}

def save_system_prompt(name: str, prompt: str):
    """Save system prompt to session state"""
    if "saved_prompts" not in st.session_state:
        st.session_state.saved_prompts = {}
    st.session_state.saved_prompts[name] = prompt

def load_system_prompt(name: str) -> str:
    """Load system prompt from session state"""
    if "saved_prompts" not in st.session_state:
        return ""
    return st.session_state.saved_prompts.get(name, "")

def main():
    init_session_state()
    client = AzureO3ProClient()
    
    # Sidebar for configuration
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # System Prompt Section
        st.subheader("System Prompt")
        
        # Predefined system prompts
        predefined_prompts = {
            "Default": """You are a helpful AI assistant powered by O3-Pro, OpenAI's most advanced reasoning model. You excel at complex problem-solving, detailed analysis, and providing thoughtful, well-reasoned responses. You think step-by-step through problems and provide clear, accurate, and helpful information.""",
            
            "Code Assistant": """You are an expert programming assistant powered by O3-Pro. You have deep knowledge of:
- Multiple programming languages (Python, JavaScript, Java, C++, etc.)
- Software architecture and design patterns
- Debugging techniques and error resolution
- Code optimization and best practices
- Testing strategies and methodologies
- Version control and development workflows

When helping with code:
1. Analyze the problem thoroughly
2. Provide clean, well-commented solutions
3. Explain your reasoning and approach
4. Suggest improvements and alternatives
5. Consider edge cases and potential issues
6. Follow industry best practices and conventions""",
            
            "Research Assistant": """You are a research assistant powered by O3-Pro, specialized in:
- Document analysis and synthesis
- Information extraction and summarization
- Critical evaluation of sources and data
- Identifying patterns and insights
- Creating comprehensive reports
- Fact-checking and verification

Your approach:
1. Thoroughly analyze all provided materials
2. Extract key information and themes
3. Cross-reference and validate findings
4. Present information in a structured, clear manner
5. Provide citations and references when applicable
6. Highlight important insights and recommendations
7. Maintain objectivity and acknowledge limitations""",
            
            "Creative Writer": """You are a creative writing assistant powered by O3-Pro. You excel at:
- Storytelling across all genres (fiction, non-fiction, poetry, scripts)
- Character development and world-building
- Plot structure and narrative techniques
- Style adaptation and voice matching
- Creative brainstorming and ideation
- Content editing and improvement
- Writing for different audiences and purposes

Your creative process:
1. Understand the writer's vision and goals
2. Offer original, engaging ideas and concepts
3. Maintain consistency in tone, style, and voice
4. Provide constructive feedback and suggestions
5. Help overcome writer's block with fresh perspectives
6. Ensure proper pacing, structure, and flow
7. Adapt to various formats and requirements""",
            
            "Data Analyst": """You are a data analysis expert powered by O3-Pro. You specialize in:
- Statistical analysis and interpretation
- Data visualization and presentation
- Pattern recognition and trend analysis
- Hypothesis testing and validation
- Predictive modeling concepts
- Data cleaning and preparation guidance
- Business intelligence insights

Your analytical approach:
1. Examine data thoroughly for quality and completeness
2. Apply appropriate statistical methods
3. Identify meaningful patterns and correlations
4. Provide clear, actionable insights
5. Explain findings in business-friendly terms
6. Suggest data collection improvements
7. Recommend next steps and follow-up analyses""",
            
            "Technical Writer": """You are a technical writing specialist powered by O3-Pro. You excel at:
- Creating clear, comprehensive documentation
- Translating complex technical concepts into accessible language
- User manuals, API documentation, and guides
- Process documentation and procedures
- Technical specifications and requirements
- Training materials and tutorials

Your documentation principles:
1. Prioritize clarity and user experience
2. Structure information logically and hierarchically
3. Use appropriate technical terminology consistently
4. Include relevant examples and use cases
5. Consider different skill levels and audiences
6. Ensure accuracy and completeness
7. Follow documentation best practices and standards"""
        }
        
        selected_preset = st.selectbox("Choose a preset:", list(predefined_prompts.keys()))
        if st.button("Load Preset"):
            st.session_state.system_prompt = predefined_prompts[selected_preset]
            st.rerun()
        
        # Custom system prompt
        st.session_state.system_prompt = st.text_area(
            "System Prompt:",
            value=st.session_state.system_prompt,
            height=150,
            help="Set the behavior and personality of the AI assistant"
        )
        
        # Save/Load custom prompts
        st.subheader("Manage Custom Prompts")
        prompt_name = st.text_input("Prompt Name:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save") and prompt_name:
                save_system_prompt(prompt_name, st.session_state.system_prompt)
                st.success(f"Saved '{prompt_name}'")
        
        with col2:
            if "saved_prompts" in st.session_state and st.session_state.saved_prompts:
                saved_prompt_names = list(st.session_state.saved_prompts.keys())
                selected_saved = st.selectbox("Load Saved:", saved_prompt_names)
                if st.button("Load") and selected_saved:
                    st.session_state.system_prompt = load_system_prompt(selected_saved)
                    st.rerun()
        
        # File Upload Section
        st.subheader("📎 File Attachments")
        uploaded_files = st.file_uploader(
            "Upload files to include in context:",
            type=['pdf', 'txt', 'docx'],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, DOCX"
        )
        
        if uploaded_files:
            st.write("Uploaded Files:")
            for file in uploaded_files:
                st.write(f"• {file.name}")
                # Process and store file content
                file_content = process_uploaded_file(file)
                if file_content:
                    st.session_state.uploaded_files_content[file.name] = file_content
        
        # Model Information
        st.subheader("🔧 Model Info")
        st.info(f"""
        **Model:** {client.model}
        **Endpoint:** {client.endpoint.split('//')[1].split('.')[0]}
        **API Version:** {client.api_version}
        """)
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.uploaded_files_content = {}
            st.rerun()
    
    # Main chat interface
    st.title("🤖 O3-Pro Azure Chat")
    st.markdown("Chat with O3-Pro model hosted on Azure OpenAI")
    
    # Display current system prompt
    with st.expander("Current System Prompt", expanded=False):
        st.markdown(f"```\n{st.session_state.system_prompt}\n```")
    
    # Display uploaded files content
    if st.session_state.uploaded_files_content:
        with st.expander(f"Attached Files ({len(st.session_state.uploaded_files_content)})", expanded=False):
            for filename, content in st.session_state.uploaded_files_content.items():
                st.subheader(filename)
                st.text_area(
                    f"Content of {filename}:",
                    value=content[:1000] + "..." if len(content) > 1000 else content,
                    height=200,
                    disabled=True
                )
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare messages for API call
        messages = [{"role": "system", "content": st.session_state.system_prompt}]
        
        # Add file contents to system message if any
        if st.session_state.uploaded_files_content:
            file_context = "\n\nAttached files content:\n"
            for filename, content in st.session_state.uploaded_files_content.items():
                file_context += f"\n--- {filename} ---\n{content}\n"
            messages[0]["content"] += file_context
        
        # Add conversation history
        messages.extend(st.session_state.messages)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                with st.spinner("Thinking..."):
                    # First try non-streaming for O3-Pro
                    response = client.create_chat_completion(messages, stream=False)
                    
                    if response and 'output' in response:
                        # Parse O3-Pro response format
                        content = client._extract_content_from_o3_response(response)
                        if content:
                            message_placeholder.markdown(content)
                            full_response = content
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                        else:
                            st.error("No content found in O3-Pro response")
                    else:
                        st.error("Failed to get response from O3-Pro model")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Powered by Azure OpenAI O3-Pro | Built with Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
