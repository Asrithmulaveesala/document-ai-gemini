import { useState, useEffect } from "react";

import {
  Plus,
  MessageSquare,
  FileText,
  Upload,
  Trash2,
  Send,
  Sparkles,
  MoreHorizontal,
  CheckCircle2,
  Database,
  Menu,
  X,
} from "lucide-react";

import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  // ============================================================
  // SESSIONS
  // ============================================================

  const [sessions, setSessions] = useState(() => {
    const savedSessions = localStorage.getItem("document_ai_sessions");

    if (savedSessions) {
      try {
        return JSON.parse(savedSessions);
      } catch {
        return [];
      }
    }

    return [
      {
        id: "chat_1",
        name: "New conversation",
        messages: [],
      },
    ];
  });

  const [currentSessionId, setCurrentSessionId] = useState(() => {
    const savedCurrentSession = localStorage.getItem(
      "document_ai_current_session"
    );

    return savedCurrentSession || "chat_1";
  });

  // ============================================================
  // DOCUMENT STATE
  // ============================================================

  const [uploadedFiles, setUploadedFiles] = useState([]);

  const [documentsProcessed, setDocumentsProcessed] = useState(false);

  const [chunkCount, setChunkCount] = useState(0);

  // ============================================================
  // CHAT STATE
  // ============================================================

  const [inputText, setInputText] = useState("");

  const [chatLoading, setChatLoading] = useState(false);

  // ============================================================
  // UI STATE
  // ============================================================

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [processing, setProcessing] = useState(false);

  // ============================================================
  // SAVE SESSIONS LOCALLY
  // ============================================================

  useEffect(() => {
    localStorage.setItem(
      "document_ai_sessions",
      JSON.stringify(sessions)
    );
  }, [sessions]);

  useEffect(() => {
    localStorage.setItem(
      "document_ai_current_session",
      currentSessionId
    );
  }, [currentSessionId]);

  // ============================================================
  // ENSURE CURRENT SESSION EXISTS
  // ============================================================

  useEffect(() => {
    const exists = sessions.some(
      (session) => session.id === currentSessionId
    );

    if (!exists) {
      setCurrentSessionId(
        sessions.length > 0 ? sessions[0].id : "chat_1"
      );
    }
  }, [sessions, currentSessionId]);

  // ============================================================
  // CURRENT SESSION
  // ============================================================

  const currentSession =
    sessions.find(
      (session) => session.id === currentSessionId
    ) || {
      id: currentSessionId,
      name: "New conversation",
      messages: [],
    };

  // ============================================================
  // LOAD SESSION MESSAGES FROM FASTAPI
  // ============================================================

  const loadSessionMessages = async (sessionId) => {
    try {
      const response = await fetch(
        `${API_URL}/sessions/${sessionId}/messages`
      );

      if (!response.ok) {
        throw new Error("Failed to load messages");
      }

      const data = await response.json();

      setSessions((previous) =>
        previous.map((session) =>
          session.id === sessionId
            ? {
                ...session,
                messages: data.map((message) => ({
                  role: message.role,
                  content: message.content,
                })),
              }
            : session
        )
      );
    } catch (error) {
      console.error(
        "Failed to load session messages:",
        error
      );
    }
  };

  // ============================================================
  // NEW CHAT
  // ============================================================

  const createNewChat = () => {
    const newSession = {
      id: `chat_${Date.now()}`,
      name: "New conversation",
      messages: [],
    };

    setSessions((previous) => [
      ...previous,
      newSession,
    ]);

    setCurrentSessionId(newSession.id);

    if (window.innerWidth < 800) {
      setSidebarOpen(false);
    }
  };

  // ============================================================
  // DELETE CHAT
  // ============================================================

  const deleteCurrentChat = (event) => {
    event.stopPropagation();

    if (sessions.length === 1) {
      const newSession = {
        id: "chat_1",
        name: "New conversation",
        messages: [],
      };

      setSessions([newSession]);
      setCurrentSessionId("chat_1");

      return;
    }

    const remaining = sessions.filter(
      (session) =>
        session.id !== currentSessionId
    );

    setSessions(remaining);
    setCurrentSessionId(remaining[0].id);
  };

  // ============================================================
  // FILE UPLOAD
  // ============================================================

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);

    if (files.length === 0) {
      return;
    }

    // Current FastAPI backend processes one PDF at a time.
    const pdfFile = files.find(
      (file) =>
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf")
    );

    if (!pdfFile) {
      alert("Please select a PDF file.");
      return;
    }

    setUploadedFiles([pdfFile]);

    setDocumentsProcessed(false);

    setChunkCount(0);

    event.target.value = "";
  };

  // ============================================================
  // PROCESS DOCUMENT
  // ============================================================

  const processDocuments = async () => {
    if (uploadedFiles.length === 0) {
      return;
    }

    setProcessing(true);

    try {
      const file = uploadedFiles[0];

      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.error ||
            "Failed to process document"
        );
      }

      console.log("Upload response:", data);

      setDocumentsProcessed(true);

      setChunkCount(data.chunks);

    } catch (error) {
      console.error(
        "Upload error:",
        error
      );

      alert(
        error.message ||
          "Failed to process the document. Check the FastAPI server."
      );
    } finally {
      setProcessing(false);
    }
  };

  // ============================================================
  // SEND MESSAGE
  // ============================================================

  const sendMessage = async () => {
    if (
      !inputText.trim() ||
      !documentsProcessed ||
      chatLoading
    ) {
      return;
    }

    const question = inputText.trim();

    const userMessage = {
      role: "user",
      content: question,
    };

    let chatName = currentSession.name;

    if (chatName === "New conversation") {
      chatName =
        question.length > 32
          ? question.substring(0, 32) + "..."
          : question;
    }

    // ========================================================
    // ADD USER MESSAGE
    // ========================================================

    setSessions((previous) =>
      previous.map((session) =>
        session.id === currentSessionId
          ? {
              ...session,
              name: chatName,
              messages: [
                ...session.messages,
                userMessage,
              ],
            }
          : session
      )
    );

    setInputText("");

    setChatLoading(true);

    // ========================================================
    // ADD EMPTY ASSISTANT MESSAGE
    // ========================================================

    setSessions((previous) =>
      previous.map((session) =>
        session.id === currentSessionId
          ? {
              ...session,
              messages: [
                ...session.messages,
                {
                  role: "assistant",
                  content: "",
                },
              ],
            }
          : session
      )
    );

    try {
      // ======================================================
      // SEND REQUEST TO FASTAPI
      // ======================================================

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question: question,
            session_id: currentSessionId,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          errorText || "Chat request failed"
        );
      }

      if (!response.body) {
        throw new Error(
          "Streaming response is not available."
        );
      }

      // ======================================================
      // STREAM RESPONSE
      // ======================================================

      const reader =
        response.body.getReader();

      const decoder =
        new TextDecoder();

      let answer = "";

      while (true) {
        const {
          value,
          done,
        } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(
          value,
          {
            stream: true,
          }
        );

        answer += chunk;

        // ====================================================
        // UPDATE ASSISTANT MESSAGE
        // ====================================================

        setSessions((previous) =>
          previous.map((session) => {
            if (
              session.id !==
              currentSessionId
            ) {
              return session;
            }

            const updatedMessages = [
              ...session.messages,
            ];

            const lastMessageIndex =
              updatedMessages.length - 1;

            updatedMessages[
              lastMessageIndex
            ] = {
              ...updatedMessages[
                lastMessageIndex
              ],
              content: answer,
            };

            return {
              ...session,
              messages: updatedMessages,
            };
          })
        );
      }

      // ======================================================
      // FLUSH DECODER
      // ======================================================

      answer += decoder.decode();

      // ======================================================
      // FINAL ASSISTANT RESPONSE
      // ======================================================

      setSessions((previous) =>
        previous.map((session) => {
          if (
            session.id !==
            currentSessionId
          ) {
            return session;
          }

          const updatedMessages = [
            ...session.messages,
          ];

          const lastMessageIndex =
            updatedMessages.length - 1;

          updatedMessages[
            lastMessageIndex
          ] = {
            ...updatedMessages[
              lastMessageIndex
            ],
            content: answer,
          };

          return {
            ...session,
            messages: updatedMessages,
          };
        })
      );

    } catch (error) {
      console.error(
        "Chat streaming error:",
        error
      );

      setSessions((previous) =>
        previous.map((session) => {
          if (
            session.id !==
            currentSessionId
          ) {
            return session;
          }

          const updatedMessages = [
            ...session.messages,
          ];

          const lastMessageIndex =
            updatedMessages.length - 1;

          if (
            lastMessageIndex >= 0 &&
            updatedMessages[
              lastMessageIndex
            ].role === "assistant"
          ) {
            updatedMessages[
              lastMessageIndex
            ] = {
              ...updatedMessages[
                lastMessageIndex
              ],
              content:
                "Sorry, I couldn't get a response from the AI backend.",
            };
          }

          return {
            ...session,
            messages: updatedMessages,
          };
        })
      );

    } finally {
      setChatLoading(false);
    }
  };

  // ============================================================
  // ENTER KEY
  // ============================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="app">

      {/* ======================================================
          MOBILE OVERLAY
      ====================================================== */}

      {sidebarOpen && (
        <div
          className="mobile-overlay"
          onClick={() =>
            setSidebarOpen(false)
          }
        />
      )}

      {/* ======================================================
          SIDEBAR
      ====================================================== */}

      <aside
        className={`sidebar ${
          sidebarOpen ? "open" : ""
        }`}
      >

        {/* BRAND */}

        <div className="brand">

          <div className="brand-icon">
            <Sparkles size={19} />
          </div>

          <div>
            <div className="brand-name">
              Document AI
            </div>

            <div className="brand-version">
              Intelligent workspace
            </div>
          </div>

          <button
            className="mobile-close"
            onClick={() =>
              setSidebarOpen(false)
            }
          >
            <X size={18} />
          </button>

        </div>

        {/* NEW CHAT */}

        <button
          className="new-chat"
          onClick={createNewChat}
        >
          <Plus size={17} />

          <span>
            New conversation
          </span>
        </button>

        {/* RECENT */}

        <div className="sidebar-section">

          <div className="section-label">
            RECENT
          </div>

          <div className="session-list">

            {sessions.map(
              (session) => (

                <div
                  key={session.id}
                  className={`session ${
                    session.id ===
                    currentSessionId
                      ? "selected"
                      : ""
                  }`}
                  onClick={async () => {

                    setCurrentSessionId(
                      session.id
                    );

                    await loadSessionMessages(
                      session.id
                    );

                    if (
                      window.innerWidth <
                      800
                    ) {
                      setSidebarOpen(
                        false
                      );
                    }
                  }}
                >

                  <MessageSquare
                    size={16}
                  />

                  <span className="session-name">
                    {session.name}
                  </span>

                  {session.id ===
                    currentSessionId && (

                    <button
                      className="session-menu"
                      onClick={
                        deleteCurrentChat
                      }
                      title="Delete conversation"
                    >
                      <Trash2
                        size={14}
                      />
                    </button>

                  )}

                </div>

              )
            )}

          </div>

        </div>

        {/* DOCUMENTS */}

        <div className="sidebar-section documents-section">

          <div className="section-label">
            KNOWLEDGE BASE
          </div>

          <div className="document-card">

            <div className="document-card-header">

              <div className="document-icon">
                <Database size={17} />
              </div>

              <div>

                <div className="document-title">
                  Your documents
                </div>

                <div className="document-subtitle">
                  {documentsProcessed
                    ? "Knowledge base ready"
                    : "No documents added"}
                </div>

              </div>

            </div>

            {/* UPLOAD */}

            <label className="upload-area">

              <Upload size={19} />

              <span>
                Upload PDF
              </span>

              <small>
                One PDF at a time
              </small>

              <input
                type="file"
                accept=".pdf"
                onChange={
                  handleFileUpload
                }
              />

            </label>

            {/* FILES */}

            {uploadedFiles.length >
              0 && (

              <div className="file-list">

                {uploadedFiles.map(
                  (file) => (

                    <div
                      className="file-row"
                      key={file.name}
                    >

                      <FileText
                        size={15}
                      />

                      <span>
                        {file.name}
                      </span>

                    </div>

                  )
                )}

              </div>

            )}

            {/* PROCESS */}

            {uploadedFiles.length >
              0 &&
              !documentsProcessed && (

                <button
                  className="process-button"
                  onClick={
                    processDocuments
                  }
                  disabled={processing}
                >
                  {processing
                    ? "Processing..."
                    : "Process document"}
                </button>

              )}

            {/* READY */}

            {documentsProcessed && (

              <div className="ready-status">

                <CheckCircle2
                  size={16}
                />

                <div>

                  <strong>
                    Knowledge base ready
                  </strong>

                  <span>
                    {uploadedFiles.length}{" "}
                    {uploadedFiles.length ===
                    1
                      ? "document"
                      : "documents"}{" "}
                    · {chunkCount} chunks
                  </span>

                </div>

              </div>

            )}

          </div>

        </div>

        {/* SIDEBAR FOOTER */}

        <div className="sidebar-footer">

          <div className="footer-status">

            <span className="online-dot"></span>

            <span>
              AI workspace
            </span>

          </div>

        </div>

      </aside>

      {/* ======================================================
          MAIN
      ====================================================== */}

      <main className="main">

        {/* TOP BAR */}

        <header className="topbar">

          <button
            className="menu-button"
            onClick={() =>
              setSidebarOpen(true)
            }
          >
            <Menu size={20} />
          </button>

          <div className="mobile-brand">

            <Sparkles size={17} />

            <span>
              Document AI
            </span>

          </div>

          <div className="topbar-right">

            <button className="icon-button">

              <MoreHorizontal
                size={19}
              />

            </button>

          </div>

        </header>

        {/* ====================================================
            CHAT
        ==================================================== */}

        <section className="chat-container">

          {/* EMPTY STATE */}

          {currentSession.messages.length ===
            0 && (

            <div className="empty-state">

              <div className="hero-icon">

                <Sparkles size={28} />

              </div>

              <h1>
                Ask anything about your
                documents
              </h1>

              <p>
                Upload your PDFs and let
                Document AI find the
                information you need.
              </p>

              {!documentsProcessed && (

                <div className="empty-hint">

                  <FileText size={15} />

                  <span>
                    Start by uploading a
                    document from the
                    sidebar
                  </span>

                </div>

              )}

              {documentsProcessed && (

                <div className="empty-hint ready">

                  <CheckCircle2
                    size={15}
                  />

                  <span>
                    Your document is
                    ready. Ask your first
                    question.
                  </span>

                </div>

              )}

            </div>

          )}

          {/* ==================================================
              MESSAGES
          ================================================== */}

          {currentSession.messages.length >
            0 && (

            <div className="message-list">

              {currentSession.messages.map(
                (message, index) => (

                  <div
                    key={index}
                    className={`message ${
                      message.role
                    }`}
                  >

                    {/* ASSISTANT ICON */}

                    {message.role ===
                      "assistant" && (

                      <div className="ai-avatar">

                        <Sparkles
                          size={15}
                        />

                      </div>

                    )}

                    <div className="message-body">

                      {message.role ===
                        "assistant" && (

                        <div className="message-author">
                          Document AI
                        </div>

                      )}

                      <div className="message-text">
                        {message.content}
                      </div>

                    </div>

                    {/* USER ICON */}

                    {message.role ===
                      "user" && (

                      <div className="user-avatar">
                        You
                      </div>

                    )}

                  </div>

                )
              )}

              {/* THINKING INDICATOR */}

              {chatLoading && (

                <div className="message assistant">

                  <div className="ai-avatar">

                    <Sparkles
                      size={15}
                    />

                  </div>

                  <div className="message-body">

                    <div className="message-author">
                      Document AI
                    </div>

                    <div className="message-text">
                      Thinking...
                    </div>

                  </div>

                </div>

              )}

            </div>

          )}

          {/* THINKING WHEN THERE ARE NO MESSAGES */}

          {chatLoading &&
            currentSession.messages.length ===
              0 && (

              <div className="message-list">

                <div className="message assistant">

                  <div className="ai-avatar">

                    <Sparkles
                      size={15}
                    />

                  </div>

                  <div className="message-body">

                    <div className="message-author">
                      Document AI
                    </div>

                    <div className="message-text">
                      Thinking...
                    </div>

                  </div>

                </div>

              </div>

            )}

        </section>

        {/* ====================================================
            INPUT
        ==================================================== */}

        <div className="composer-wrapper">

          <div className="composer">

            <textarea
              value={inputText}
              onChange={(event) =>
                setInputText(
                  event.target.value
                )
              }
              onKeyDown={
                handleKeyDown
              }
              placeholder={
                documentsProcessed
                  ? "Ask a question about your documents..."
                  : "Upload documents to start chatting..."
              }
              disabled={
                !documentsProcessed ||
                chatLoading
              }
              rows={1}
            />

            <button
              className="send-button"
              onClick={sendMessage}
              disabled={
                !inputText.trim() ||
                !documentsProcessed ||
                chatLoading
              }
            >
              <Send size={17} />
            </button>

          </div>

          <div className="composer-note">
            Document AI can make mistakes.
            Verify important information.
          </div>

        </div>

      </main>

    </div>
  );
}

export default App;