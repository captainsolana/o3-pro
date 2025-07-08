# O3-Pro Azure Chat Application

A Streamlit-based frontend application for chatting with the O3-Pro model hosted on Azure OpenAI.

## Features

- 🤖 **Chat Interface**: Interactive chat with O3-Pro model
- ⚙️ **System Prompt Configuration**: Set and customize system prompts
- 📎 **File Attachments**: Upload and include PDF, TXT, and DOCX files in context
- 💾 **Prompt Management**: Save and load custom system prompts
- 🎨 **Modern UI**: Clean and intuitive Streamlit interface
- 🔐 **Secure Credentials**: Environment-based credential management

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure your Azure OpenAI credentials:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual Azure OpenAI credentials:
- Set your Azure OpenAI endpoint
- Add your API key
- Configure the model name (o3-pro)
- Set the API version

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage Guide

### System Prompts
1. Use the sidebar to configure the AI's behavior
2. Choose from predefined prompts or create custom ones
3. Save frequently used prompts for quick access

### File Attachments
1. Upload files using the sidebar file uploader
2. Supported formats: PDF, TXT, DOCX
3. File content is automatically included in the conversation context

### Chat Interface
1. Type your message in the chat input
2. View conversation history with clear user/assistant distinction
3. Clear conversation using the sidebar button

## File Structure

```
o3-pro/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env               # Environment variables (create from .env.example)
└── README.md          # This file
```

## Troubleshooting

### Common Issues

1. **API Authentication Error**
   - Verify the API key in `.env` file
   - Check Azure OpenAI endpoint status

2. **File Upload Issues**
   - Ensure file formats are supported (PDF, TXT, DOCX)
   - Check file size limits

3. **Connection Errors**
   - Verify internet connection
   - Check Azure OpenAI service availability

### Error Handling

The application includes comprehensive error handling:
- API connection failures
- File processing errors
- Invalid file formats
- Rate limiting

## Security Notes

- API credentials are stored in `.env` file (not included in repository)
- Copy `.env.example` to `.env` and add your credentials
- Never commit `.env` file to version control
- Keep your API key secure and rotate it regularly
- The `.env` file is excluded via `.gitignore`

## Customization

### Adding New File Types
Extend the `process_uploaded_file()` function to support additional formats.

### Custom Styling
Modify the Streamlit configuration and CSS in the main application file.

### Additional Features
- Export conversation history
- Custom model parameters
- Multi-language support

## Support

For issues related to:
- **Azure OpenAI**: Check Azure portal and service status
- **Streamlit**: Refer to Streamlit documentation
- **File Processing**: Verify file format compatibility

## Version Information

- **Streamlit**: 1.29.0
- **OpenAI Python**: 1.7.2
- **Python**: 3.8+

Built with ❤️ using Streamlit and Azure OpenAI
