// AgentsPage.js - Updated to use orchestration agent
import React, { useState, useEffect } from "react";
import { Document, Page } from "react-pdf";
import {
  Button,
  TextField,
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import ZoomOutIcon from "@mui/icons-material/ZoomOut";
import ZoomOutMapIcon from "@mui/icons-material/ZoomOutMap";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ResizablePanels from "../components/ResizablePanels";
import { pdfjs } from "react-pdf";
import { getDocument, getProjectDocuments } from "../api/documents";
import { sendOrchestrationMessage, testOrchestrationService } from '../api/agents';
//import { testOrchestrationService, sendOrchestrationMessage } from "../services/orchestrationService";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "@mui/material/styles";
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import useRefreshRedirect from "../hooks/useRefreshRedirect";

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function AgentsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { projectId } = useParams();
  const { userId, loading: authLoading } = useAuth();
  const theme = useTheme();

  // Enable refresh redirect to home page
  useRefreshRedirect();

  // Get project and documents from navigation state
  const project = location.state?.project || {};
  const [documents, setDocuments] = useState(location.state?.documents || []);
  const [currentDocument, setCurrentDocument] = useState(
    location.state?.selectedDocument || null
  );
  const [pdfContent, setPdfContent] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [pdfError, setPdfError] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [orchestrationServiceStatus, setOrchestrationServiceStatus] =
    useState("unknown");

  // Zoom functionality state
  const [zoomLevel, setZoomLevel] = useState(1);
  const [baseWidth, setBaseWidth] = useState(400);

  useEffect(() => {
    console.log("AgentsPage useEffect triggered:", {
      projectId,
      userId,
      authLoading,
      locationState: location.state,
      documentsFromState: location.state?.documents?.length || 0,
    });

    // Don't load documents if auth is still loading
    if (authLoading) {
      console.log("⏳ Auth is still loading, waiting...");
      return;
    }

    // Test orchestration service connectivity
    checkOrchestrationService();

    // Always load all documents for the project to ensure dropdown is populated
    if (projectId && userId) {
      loadProjectDocuments();

      // If a specific document was provided from navigation state, handle it
      if (location.state?.selectedDocument) {
        // Set current document immediately and update URL
        setCurrentDocument(location.state.selectedDocument);
        const searchParams = new URLSearchParams(location.search);
        searchParams.set("document", location.state.selectedDocument.doc_id);
        navigate(`${location.pathname}?${searchParams.toString()}`, {
          replace: true,
        });

        // Load the document content
        loadSelectedDocument(location.state.selectedDocument, false);
      }
    } else if (!userId && !authLoading) {
      console.log("No userId available after auth loading completed");
    }
  }, [projectId, userId, authLoading]);

  // Separate useEffect to handle document selection from URL or navigation state
  useEffect(() => {
    // If we have documents loaded and no current document selected,
    // try to select the first document or one from URL params
    if (documents.length > 0 && !currentDocument) {
      // Check if there's a document ID in URL search params (for refresh handling)
      const urlParams = new URLSearchParams(location.search);
      const docIdFromUrl = urlParams.get("document");

      if (docIdFromUrl) {
        const docFromUrl = documents.find((doc) => doc.doc_id === docIdFromUrl);
        if (docFromUrl) {
          loadSelectedDocument(docFromUrl, false); // Don't update URL since it's already there
          return;
        }
      }

      // If no document from URL, select the first one and update URL
      loadSelectedDocument(documents[0], true);
    }
  }, [documents, location.search]);

  const checkOrchestrationService = async () => {
    try {
      const isHealthy = await testOrchestrationService();
      setOrchestrationServiceStatus(isHealthy ? "healthy" : "unhealthy");
    } catch (error) {
      console.error("Orchestration service check failed:", error);
      setOrchestrationServiceStatus("unhealthy");
    }
  };

  const loadProjectDocuments = async () => {
    if (!projectId || !userId) {
      console.error("Missing projectId or userId:", { projectId, userId });
      return;
    }

    try {
      setLoading(true);
      console.log("Loading documents for project:", projectId, "user:", userId);

      const documentsData = await getProjectDocuments(projectId, userId);
      console.log("Loaded documents:", documentsData);

      if (Array.isArray(documentsData)) {
        setDocuments(documentsData);
        console.log(
          "Set documents in state:",
          documentsData.length,
          "documents"
        );
      } else {
        console.warn("Documents data is not an array:", documentsData);
        setDocuments([]);
      }
    } catch (error) {
      console.error("Error loading project documents:", error);
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSelectedDocument = async (doc, updateUrl = false) => {
    setCurrentDocument(doc);
    setPdfLoading(true);
    setPdfError(null);

    try {
      console.log("Loading PDF for document:", doc.doc_id);
      const pdfBlob = await getDocument(projectId, doc.doc_id, userId);
      console.log("PDF blob received:", pdfBlob.size, "bytes");

      // Create a proper blob URL
      const blobUrl = URL.createObjectURL(
        new Blob([pdfBlob], { type: "application/pdf" })
      );
      console.log("Blob URL created:", blobUrl);

      setPdfContent(blobUrl);

      // Update URL if requested (for programmatic selections)
      if (updateUrl) {
        const searchParams = new URLSearchParams(location.search);
        searchParams.set("document", doc.doc_id);
        navigate(`${location.pathname}?${searchParams.toString()}`, {
          replace: true,
        });
      }
    } catch (error) {
      console.error("Error loading PDF:", error);
      setPdfError(error.message || "Failed to load PDF file");
    } finally {
      setPdfLoading(false);
    }
  };

  const handleDocumentSelect = async (event) => {
    const selectedDoc = documents.find(
      (doc) => doc.doc_id === event.target.value
    );
    if (selectedDoc) {
      // Clean up previous PDF URL to prevent memory leaks
      if (pdfContent) {
        URL.revokeObjectURL(pdfContent);
      }
      await loadSelectedDocument(selectedDoc);

      // Update URL to include selected document for refresh persistence
      const searchParams = new URLSearchParams(location.search);
      searchParams.set("document", selectedDoc.doc_id);
      navigate(`${location.pathname}?${searchParams.toString()}`, {
        replace: true,
      });
    }
  };

  // Clean up blob URLs when component unmounts
  useEffect(() => {
    return () => {
      if (pdfContent) {
        URL.revokeObjectURL(pdfContent);
      }
    };
  }, [pdfContent]);

  const handleSendMessage = async () => {
    if (!currentDocument || !prompt.trim() || sendingMessage) {
      return;
    }

    // Check orchestration service status before sending
    if (orchestrationServiceStatus === "unhealthy") {
      const errorMessage = {
        type: "agent",
        content:
          "The orchestration service is currently unavailable. Please try again later or contact support.",
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
      return;
    }

    // Add user message to chat
    const userMessage = {
      type: "user",
      content: prompt,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    const currentPrompt = prompt;
    const executionId = `exec_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    setPrompt(""); // Clear input immediately
    setSendingMessage(true);

    try {
      console.log("Sending message to orchestration agent:", {
        message: currentPrompt,
        currentDocument: currentDocument.doc_id,
        allDocuments: documents.map((doc) => doc.doc_id), // ← Show all docs
        totalDocuments: documents.length,
        userId,
        projectId,
        executionId,
      });
      const allDocumentIds = documents.map((doc) => doc.doc_id);

      // Call orchestration service with single document
      const response = await sendOrchestrationMessage(
        currentPrompt,
        allDocumentIds, // passes all documents
        userId,
        projectId,
        executionId
      );

      console.log("Received response from orchestration agent:", response);

      // Add agent message to chat with detailed information
      const agentMessage = {
        type: "agent",
        content: response.content,
        timestamp: new Date().toISOString(),
        agentId: response.agentId || "orchestration-agent",
        executionId: response.executionId,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Add error message to chat
      const errorMessage = {
        type: "agent",
        content: `I apologize, but I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);

      // If it's a service unavailable error, recheck service status
      if (
        error.message.includes("unavailable") ||
        error.message.includes("timeout")
      ) {
        checkOrchestrationService();
      }
    } finally {
      setSendingMessage(false);
    }
  };

  const handleModifyResponse = (messageIndex) => {
    const message = messages[messageIndex];
    if (message && message.type === "agent") {
      // Set the agent's response as the current prompt for modification
      setPrompt(`Please modify this response: "${message.content}"`);

      // Optionally, mark the message as being modified
      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === messageIndex ? { ...msg, beingModified: true } : msg
        )
      );
    }
  };

  const handleConfirmResponse = (messageIndex) => {
    const message = messages[messageIndex];
    if (message && message.type === "agent") {
      // Mark the response as confirmed
      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === messageIndex
            ? { ...msg, confirmed: true, beingModified: false }
            : msg
        )
      );

      console.log("Response confirmed:", message.content);
    }
  };

  // Zoom functionality handlers
  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev - 0.25, 0.5));
  };

  const handleZoomReset = () => {
    setZoomLevel(1);
  };

  // Calculate actual width based on zoom level
  const getDocumentWidth = () => {
    const maxWidth = Math.min(400, window.innerWidth * 0.35);
    return maxWidth * zoomLevel;
  };

  // Service status indicator component removed

  // Show loading state while authentication is loading
  if (authLoading) {
    return (
      <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        <Box
          sx={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 2,
          }}
        >
          <CircularProgress size={40} />
          <Typography variant="body1" color="text.secondary">
            Loading authentication...
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      width: "100%",
      height: "100%", 
      m: 0, 
      p: 2,
      display: "flex",
      alignItems: "stretch",
      justifyContent: "stretch",
      boxSizing: "border-box"
    }}>
      <Box sx={{
        width: "100%",
        height: "100%",
        border: "3px solid",
        borderColor: "primary.main",
        borderRadius: 4,
        background: "linear-gradient(135deg, rgba(124, 77, 255, 0.05) 0%, rgba(124, 77, 255, 0.02) 100%)",
        boxShadow: "0 8px 32px rgba(124, 77, 255, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08)",
        overflow: "hidden",
        position: "relative",
        boxSizing: "border-box",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(124, 77, 255, 0.05) 100%)",
          pointerEvents: "none",
          zIndex: 1
        }
      }}>
        <Box sx={{ height: "100%", width: "100%", position: "relative", zIndex: 2 }}>
          <ResizablePanels
            defaultLeftWidth={40}
            minLeftWidth={25}
            maxLeftWidth={75}
            storageKey="agents-page-panel-width"
          leftPanel={
            <Box
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                m: 1,
                p: 2,
                backgroundColor: "rgba(255, 255, 255, 0.9)",
                borderRadius: 2,
                backdropFilter: "blur(10px)",
                zIndex: 2,
                position: "relative"
              }}
            >
              {/* Document selector */}
              <Box sx={{ p: 0, m: 0, mb: 1 }}>
                <Box sx={{ mb: 0, mt: 0 }}>
                  <FormControl fullWidth sx={{ m: 0 }}>
                    <InputLabel>Select Document</InputLabel>
                    <Select
                      value={currentDocument?.doc_id || ""}
                      onChange={handleDocumentSelect}
                      label="Select Document"
                      disabled={loading || documents.length === 0}
                    >
                      {documents.map((doc) => (
                        <MenuItem key={doc.doc_id} value={doc.doc_id}>
                          {doc.title}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
                {loading && (
                  <Typography
                    variant="caption"
                    sx={{
                      mt: 1,
                      color: "text.secondary",
                      fontSize: "0.75rem",
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                    }}
                  >
                    <CircularProgress size={12} />
                    Loading documents...
                  </Typography>
                )}
              </Box>

              {/* PDF viewer */}
              <Box
                sx={{
                  flexGrow: 1,
                  overflow: pdfContent ? "auto" : "hidden",
                  p: 0,
                }}
              >
                {/* Zoom Controls */}
                {pdfContent && !loading && !pdfError && !pdfLoading && (
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      mb: 0,
                      gap: 1,
                      flexWrap: "wrap",
                    }}
                  >
                    <Tooltip title="Zoom Out">
                      <IconButton
                        onClick={handleZoomOut}
                        disabled={zoomLevel <= 0.5}
                        size="small"
                      >
                        <ZoomOutIcon />
                      </IconButton>
                    </Tooltip>

                    <Typography
                      variant="body2"
                      sx={{
                        minWidth: "60px",
                        textAlign: "center",
                        fontWeight: "medium",
                      }}
                    >
                      {Math.round(zoomLevel * 100)}%
                    </Typography>

                    <Tooltip title="Zoom In">
                      <IconButton
                        onClick={handleZoomIn}
                        disabled={zoomLevel >= 3}
                        size="small"
                      >
                        <ZoomInIcon />
                      </IconButton>
                    </Tooltip>

                    <Tooltip title="Reset Zoom (100%)">
                      <IconButton onClick={handleZoomReset} size="small">
                        <ZoomOutMapIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                )}

                {loading ? (
                  <Paper sx={{ p: 4, textAlign: "center" }}>
                    <CircularProgress sx={{ mb: 2 }} />
                    <Typography>Loading documents...</Typography>
                  </Paper>
                ) : pdfError ? (
                  <Paper sx={{ p: 4, textAlign: "center" }}>
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {pdfError}
                    </Alert>
                    <Button
                      variant="outlined"
                      onClick={() =>
                        currentDocument && loadSelectedDocument(currentDocument)
                      }
                      disabled={pdfLoading}
                    >
                      Retry Loading PDF
                    </Button>
                  </Paper>
                ) : pdfLoading ? (
                  <Paper sx={{ p: 4, textAlign: "center" }}>
                    <CircularProgress sx={{ mb: 2 }} />
                    <Typography>Loading PDF...</Typography>
                  </Paper>
                ) : pdfContent ? (
                  <Document
                    file={pdfContent}
                    onLoadSuccess={({ numPages }) => {
                      console.log("PDF loaded successfully, pages:", numPages);
                      setNumPages(numPages);
                      setPdfError(null);
                    }}
                    onLoadError={(error) => {
                      console.error("PDF load error:", error);
                      setPdfError(
                        `Failed to load PDF: ${error.message || "Unknown error"}`
                      );
                    }}
                    loading={
                      <Paper sx={{ p: 4, textAlign: "center" }}>
                        <CircularProgress sx={{ mb: 2 }} />
                        <Typography>Loading PDF...</Typography>
                      </Paper>
                    }
                    error={
                      <Paper sx={{ p: 4, textAlign: "center" }}>
                        <Alert severity="error">
                          Failed to load PDF file. Please try again.
                        </Alert>
                      </Paper>
                    }
                  >
                    {Array.from(new Array(numPages), (_, index) => (
                      <Page
                        key={`page_${index + 1}`}
                        pageNumber={index + 1}
                        width={getDocumentWidth()}
                        renderTextLayer={false}
                        renderAnnotationLayer={false}
                      />
                    ))}
                  </Document>
                ) : documents.length === 0 ? (
                  <Paper sx={{ p: 4, textAlign: "center" }}>
                  </Paper>
                ) : (
                  <Paper sx={{ p: 4, textAlign: "center" }}>
                    <Typography color="text.secondary">
                    </Typography>
                  </Paper>
                )}
              </Box>
            </Box>
          }
          rightPanel={
            <Box
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                m: 1,
                p: 2,
                backgroundColor: "rgba(255, 255, 255, 0.9)",
                borderRadius: 2,
                backdropFilter: "blur(10px)",
                zIndex: 2,
                position: "relative"
              }}
            >
              {/* Chat messages area */}
              <Box
                sx={{
                  flexGrow: 1,
                  p: 0,
                  overflow: "hidden",
                  backgroundColor: "transparent",
                  display: "flex",
                  flexDirection: "column",
                  gap: 0,
                }}
              >
                {messages.length === 0 ? (
                  <Box
                    sx={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                    }}
                  >
                  </Box>
                ) : (
                  <Box
                    sx={{
                      flexGrow: 1,
                      overflow: "auto",
                      display: "flex",
                      flexDirection: "column",
                      gap: 0.5,
                    }}
                  >
                    {messages.map((message, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: "flex",
                      justifyContent:
                        message.type === "user" ? "flex-end" : "flex-start",
                      width: "100%",
                    }}
                  >
                    <Box sx={{ maxWidth: "85%", width: "100%" }}>
                      <Paper
                        elevation={1}
                        sx={{
                          p: 1.5,
                          backgroundColor:
                            message.type === "user"
                              ? theme.palette.primary.main
                              : message.isError
                              ? "#ffebee"
                              : message.confirmed
                              ? "#e8f5e8"
                              : message.beingModified
                              ? "#fff3e0"
                              : "#fff",
                          color:
                            message.type === "user"
                              ? "#fff"
                              : message.isError
                              ? "#c62828"
                              : message.confirmed
                              ? "#2e7d32"
                              : "inherit",
                          borderRadius:
                            message.type === "user"
                              ? "20px 20px 5px 20px"
                              : "20px 20px 20px 5px",
                          border: message.isError
                            ? "1px solid #e57373"
                            : message.confirmed
                            ? "1px solid #81c784"
                            : message.beingModified
                            ? "1px solid #ffb74d"
                            : "none",
                        }}
                      >
                        <Typography
                          variant="body1"
                          sx={{
                            whiteSpace: "pre-wrap",
                            wordWrap: "break-word",
                          }}
                        >
                          {message.content}
                        </Typography>

                        {/* Status indicators */}
                        {message.confirmed && (
                          <Typography
                            variant="caption"
                            sx={{
                              display: "block",
                              mt: 1,
                              color: "#2e7d32",
                              fontWeight: "bold",
                              fontSize: "0.7rem",
                            }}
                          >
                            ✓ Confirmed
                          </Typography>
                        )}

                        {message.beingModified && (
                          <Typography
                            variant="caption"
                            sx={{
                              display: "block",
                              mt: 1,
                              color: "#f57c00",
                              fontWeight: "bold",
                              fontSize: "0.7rem",
                            }}
                          >
                            ✏️ Being modified...
                          </Typography>
                        )}

                        {message.timestamp && (
                          <Typography
                            variant="caption"
                            sx={{
                              display: "block",
                              mt: 1,
                              opacity: 0.7,
                              fontSize: "0.7rem",
                            }}
                          >
                            {new Date(message.timestamp).toLocaleTimeString()}
                            {message.executionId && (
                              <span style={{ marginLeft: "8px" }}>
                                ID: {message.executionId.split("_")[2]}
                              </span>
                            )}
                          </Typography>
                        )}
                      </Paper>

                      {/* Action buttons for agent responses */}
                      {message.type === "agent" && !message.isError && (
                        <Box
                          sx={{
                            display: "flex",
                            gap: 1,
                            mt: 1,
                            justifyContent: "flex-start",
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              color: "text.secondary",
                              fontSize: "0.7rem",
                              fontStyle: "italic",
                            }}
                          >
                            Analysis completed using AI orchestration
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Box>
                ))}

                {sendingMessage && (
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "flex-start",
                      width: "100%",
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        backgroundColor: "#fff",
                        borderRadius: "20px 20px 20px 5px",
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                      }}
                    >
                      <CircularProgress size={16} />
                      <Typography variant="body2" color="text.secondary">
                        Orchestrating AI agents...
                      </Typography>
                    </Paper>
                  </Box>
                )}
                  </Box>
                )}
              </Box>

              {/* Input area */}
              <Paper
                sx={{
                  p: 0.5,
                  backgroundColor: "#fff",
                  boxShadow: "none",
                }}
              >
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder={
                    currentDocument
                      ? `Ask for analysis across ${documents.length} document${documents.length > 1 ? 's' : ''} (viewing: "${currentDocument.title}")...`
                      : 'Select a document to start AI-powered legal analysis...'
                  }
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  variant="outlined"
                  disabled={
                    !currentDocument ||
                    sendingMessage ||
                    orchestrationServiceStatus === "unhealthy"
                  }
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <Box sx={{ 
                        display: "flex", 
                        flexDirection: "column", 
                        alignItems: "flex-end",
                        gap: 1,
                        ml: 1
                      }}>
                        <Button
                          variant="contained"
                          disabled={
                            !currentDocument ||
                            !prompt.trim() ||
                            sendingMessage ||
                            orchestrationServiceStatus === "unhealthy"
                          }
                          onClick={handleSendMessage}
                          startIcon={
                            sendingMessage ? (
                              <CircularProgress size={16} />
                            ) : null
                          }
                          sx={{ 
                            minWidth: "100px",
                            height: "36px"
                          }}
                        >
                          {sendingMessage ? "Analyzing..." : "Analyze"}
                        </Button>
                        <Typography variant="caption" color="text.secondary" sx={{ fontSize: "0.7rem" }}>
                          {currentDocument
                            ? "Enter to send, Shift+Enter for new line"
                            : ""}
                        </Typography>
                      </Box>
                    )
                  }}
                />
              </Paper>
            </Box>
          }
        />
        </Box>
      </Box>
    </Box>
  );
}
