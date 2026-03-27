// Fixed Projects.js
import React, { useState, useContext, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Box,
  Typography,
  CardContent,
  Tooltip,
  Alert,
  CircularProgress,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import { Chip } from '@mui/material';
import { alpha } from '@mui/material/styles';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AddIcon from '@mui/icons-material/Add';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import DescriptionIcon from '@mui/icons-material/Description';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import { getUserProjects } from '../api/documents';
import useRefreshRedirect from '../hooks/useRefreshRedirect';

// Import shared components
import {
  HeaderActionButton,
  ActionButton,
  CreateButton,
} from '../components/Buttons';
import { ProjectCard } from '../components/Cards';
import { StyledTextField } from '../components/TextFields';
import { PageBackground, PageHeader, PageContent } from '../components/Layout';
import { StyledModal } from '../components/Modals';
import { Fade } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';

export default function Projects() {
  const navigate = useNavigate();
  const { theme } = useContext(ThemeContext);

  const [projects, setProjects] = useState([]);
  const [filteredProjects, setFilteredProjects] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [creating, setCreating] = useState(false);
  const [userAuthenticated, setUserAuthenticated] = useState(false);

  const { userId, loading: authLoading } = useAuth();

  // Enable refresh redirect to home page
  useRefreshRedirect();

  // Load projects on component mount
  useEffect(() => {
    // Don't load projects if auth is still loading
    if (authLoading) {
      console.log('⏳ Auth is still loading, waiting...');
      return;
    }

    if (userId) {
      console.log('🔄 Loading projects for user:', userId);
      loadProjects();
    } else {
      console.log('❌ No userId available after auth loading completed');
      setLoading(false);
      setUserAuthenticated(false);
    }
  }, [userId, authLoading]);

  // Filter projects based on search query
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredProjects(projects);
    } else {
      const filtered = projects.filter((project) =>
        project.project_id.toLowerCase().includes(searchQuery.toLowerCase()),
      );
      setFilteredProjects(filtered);
    }
  }, [projects, searchQuery]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError('');

      // Check if userId is available first
      if (!userId) {
        setUserAuthenticated(false);
        setProjects([]);
        setError('Please log in to view your projects.');
        return;
      }

      const projectsData = await getUserProjects(userId);

      // getUserProjects should always return an array if successful
      if (Array.isArray(projectsData)) {
        setProjects(projectsData);
        setUserAuthenticated(true);
        setError(''); // Clear any previous errors
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Error loading projects:', err);
      setProjects([]);
      setUserAuthenticated(false);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProjectName.trim()) return;

    try {
      setCreating(true);
      setError('');

      if (!userAuthenticated) {
        setError('Please log in to create projects.');
        return;
      }

      // Create project locally - it will be persisted when first document is uploaded
      const newProject = {
        project_id: newProjectName.trim(),
        document_count: 0,
      };

      setProjects((prev) => [...prev, newProject]);
      setCreateModalOpen(false);
      setNewProjectName('');

      // Navigate to the new project immediately
      navigate(`/documents/${encodeURIComponent(newProject.project_id)}`, {
        state: { project: newProject },
      });
    } catch (err) {
      console.error('Error creating project:', err);
      setError('Failed to create project. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const openProject = (project) => {
    navigate(`/documents/${encodeURIComponent(project.project_id)}`, {
      state: { project },
    });
  };

  const openInAgents = (project) => {
    navigate(`/agents/${encodeURIComponent(project.project_id)}`, {
      state: {
        project,
        // We'll load documents in the AgentsPage since we don't have them here
      },
    });
  };

  const goBack = () => {
    navigate('/dashboard');
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleRetryLoad = () => {
    setError('');
    loadProjects();
  };

  // Show loading state while authentication is loading
  if (authLoading) {
    return (
      <PageBackground>
        <PageHeader>
          <Box></Box>
        </PageHeader>
        <PageContent>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '60vh',
              gap: 2,
            }}
          >
            <CircularProgress size={40} />
            <Typography variant="body1" color="text.secondary">
              Loading authentication...
            </Typography>
          </Box>
        </PageContent>
      </PageBackground>
    );
  }

  return (
    <PageBackground>
      {/* Header */}
      <PageHeader>
        <Box></Box>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {/* TEST MODE: User ID Display */}
          {userId && (
            <Chip
              icon={<PersonIcon />}
              label={`User: ${userId.slice(0, 8)}...`}
              variant="outlined"
              size="small"
              sx={{
                bgcolor:
                  theme.palette.mode === 'dark'
                    ? alpha(theme.palette.primary.main, 0.1)
                    : alpha(theme.palette.primary.main, 0.05),
                borderColor: theme.palette.primary.main,
                color: theme.palette.primary.main,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
              }}
            />
          )}

          <Tooltip title="Torna al Dashboard" arrow>
            <HeaderActionButton onClick={goBack}>
              <ArrowBackIcon />
            </HeaderActionButton>
          </Tooltip>
        </Box>
      </PageHeader>

      {/* Main Content */}
      <PageContent>
        <Fade in timeout={1000}>
          <Box>
            {/* Page Title */}
            <Box
              sx={{
                mb: 4,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <FolderOpenIcon
                sx={{
                  fontSize: '2rem',
                  color: theme.palette.primary.main,
                }}
              />
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' },
                  color:
                    theme.palette.mode === 'dark'
                      ? theme.palette.primary.light
                      : theme.palette.primary.main,
                  letterSpacing: '-0.02em',
                }}
              >
                Projects
              </Typography>
            </Box>

            {/* Search and Create Section - Only show if user is authenticated */}
            {userAuthenticated && (
              <Box sx={{ mb: 4 }}>
                <ProjectCard>
                  <CardContent sx={{ p: 2.5 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        flexWrap: { xs: 'wrap', sm: 'nowrap' },
                      }}
                    >
                      <SearchIcon
                        sx={{
                          color:
                            theme.palette.mode === 'dark'
                              ? alpha('#FFFFFF', 0.7)
                              : alpha('#14142B', 0.7),
                          fontSize: '1.1rem',
                        }}
                      />
                      <StyledTextField
                        fullWidth
                        value={searchQuery}
                        onChange={handleSearchChange}
                        placeholder="Search projects..."
                        size="small"
                        sx={{ maxWidth: '300px' }}
                      />
                      <CreateButton
                        onClick={() => setCreateModalOpen(true)}
                        startIcon={<AddIcon />}
                        sx={{ minWidth: 'fit-content' }}
                      >
                        Create Project
                      </CreateButton>
                    </Box>
                  </CardContent>
                </ProjectCard>
              </Box>
            )}

            {/* Error Alert */}
            {error && (
              <Alert
                severity="error"
                sx={{ mb: 3 }}
                action={
                  <ActionButton size="small" onClick={handleRetryLoad}>
                    Retry
                  </ActionButton>
                }
              >
                {error}
              </Alert>
            )}

            {/* Loading State */}
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading projects...</Typography>
              </Box>
            ) : (
              <>
                {/* Projects Grid */}
                {userAuthenticated && filteredProjects.length > 0 && (
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: {
                        xs: '1fr',
                        md: 'repeat(2, 1fr)',
                      },
                      gap: 2,
                    }}
                  >
                    {filteredProjects.map((project) => (
                      <ProjectCard key={project.project_id}>
                        <CardContent
                          sx={{
                            p: 2.5,
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                          }}
                        >
                          <Box
                            sx={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'flex-start',
                              mb: 2,
                            }}
                          >
                            <Box sx={{ flex: 1 }}>
                              <Typography
                                variant="h5"
                                sx={{
                                  fontWeight: 700,
                                  fontSize: '1rem',
                                  color:
                                    theme.palette.mode === 'dark'
                                      ? '#FFFFFF'
                                      : '#14142B',
                                  mb: 1,
                                }}
                              >
                                {project.project_id}
                              </Typography>
                              <Typography
                                variant="body2"
                                sx={{
                                  color:
                                    theme.palette.mode === 'dark'
                                      ? alpha('#FFFFFF', 0.7)
                                      : alpha('#14142B', 0.7),
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1,
                                  fontSize: '0.75rem',
                                }}
                              >
                                <DescriptionIcon sx={{ fontSize: '0.85rem' }} />
                                {project.document_count || 0} document
                                {(project.document_count || 0) !== 1 ? 's' : ''}
                              </Typography>
                            </Box>
                            <ActionButton onClick={() => openProject(project)}>
                              Open Project
                            </ActionButton>
                          </Box>

                          {/* Project Info */}
                          <Box sx={{ flex: 1 }}>
                            <Box
                              sx={{
                                p: 1.5,
                                backgroundColor:
                                  theme.palette.mode === 'dark'
                                    ? alpha('#FFFFFF', 0.05)
                                    : alpha('#000000', 0.02),
                                borderRadius: '8px',
                                border: `1px solid ${theme.palette.mode === 'dark' ? alpha('#FFFFFF', 0.1) : alpha('#000000', 0.1)}`,
                              }}
                            >
                              <Typography
                                variant="body2"
                                sx={{
                                  fontWeight: 600,
                                  mb: 0.5,
                                  fontSize: '0.7rem',
                                  color:
                                    theme.palette.mode === 'dark'
                                      ? alpha('#FFFFFF', 0.8)
                                      : alpha('#14142B', 0.8),
                                }}
                              >
                                Project ID: {project.project_id}
                              </Typography>
                              <Typography
                                variant="body2"
                                sx={{
                                  fontSize: '0.65rem',
                                  color:
                                    theme.palette.mode === 'dark'
                                      ? alpha('#FFFFFF', 0.6)
                                      : alpha('#14142B', 0.6),
                                }}
                              >
                                {(project.document_count || 0) === 0
                                  ? 'No documents yet - upload your first document to get started!'
                                  : `Contains ${project.document_count} documents`}
                              </Typography>
                            </Box>
                          </Box>

                          {/* New Chat Button - Only show if there are documents */}
                          {project.document_count > 0 && (
                            <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                              <Tooltip title="Chat with Documents" arrow>
                                <ActionButton
                                  onClick={() => openInAgents(project)}
                                  startIcon={<ChatIcon />}
                                  sx={{ mr: 1 }}
                                >
                                  Chat
                                </ActionButton>
                              </Tooltip>
                              <ActionButton onClick={() => openProject(project)}>
                                Open Project
                              </ActionButton>
                            </Box>
                          )}
                        </CardContent>
                      </ProjectCard>
                    ))}
                  </Box>
                )}

                {/* No Projects Message */}
                {userAuthenticated &&
                  filteredProjects.length === 0 &&
                  !loading && (
                    <Box
                      sx={{
                        textAlign: 'center',
                        py: 6,
                        color:
                          theme.palette.mode === 'dark'
                            ? alpha('#FFFFFF', 0.6)
                            : alpha('#14142B', 0.6),
                      }}
                    >
                      <FolderOpenIcon
                        sx={{ fontSize: '3rem', mb: 2, opacity: 0.3 }}
                      />
                      <Typography
                        variant="h6"
                        sx={{ mb: 1, fontSize: '1.1rem' }}
                      >
                        {searchQuery ? 'No projects found' : 'No projects yet'}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ fontSize: '0.85rem', mb: 3 }}
                      >
                        {searchQuery
                          ? 'Try adjusting your search terms'
                          : 'Create your first project to get started'}
                      </Typography>
                      {!searchQuery && (
                        <CreateButton
                          onClick={() => setCreateModalOpen(true)}
                          startIcon={<AddIcon />}
                        >
                          Create Your First Project
                        </CreateButton>
                      )}
                    </Box>
                  )}

                {/* Not Authenticated Message */}
                {!userAuthenticated && !loading && (
                  <Box
                    sx={{
                      textAlign: 'center',
                      py: 6,
                      color:
                        theme.palette.mode === 'dark'
                          ? alpha('#FFFFFF', 0.6)
                          : alpha('#14142B', 0.6),
                    }}
                  >
                    <FolderOpenIcon
                      sx={{ fontSize: '3rem', mb: 2, opacity: 0.3 }}
                    />
                    <Typography variant="h6" sx={{ mb: 1, fontSize: '1.1rem' }}>
                      Authentication Required
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ fontSize: '0.85rem', mb: 3 }}
                    >
                      Please log in to view and manage your projects
                    </Typography>
                    <ActionButton onClick={handleRetryLoad}>
                      Try Again
                    </ActionButton>
                  </Box>
                )}
              </>
            )}
          </Box>
        </Fade>
      </PageContent>

      {/* Create Project Modal */}
      <StyledModal
        open={createModalOpen}
        onClose={() => !creating && setCreateModalOpen(false)}
        title="Create New Project"
      >
        <Box sx={{ mt: 2 }}>
          <Typography
            variant="body2"
            sx={{
              mb: 2,
              color:
                theme.palette.mode === 'dark'
                  ? alpha('#FFFFFF', 0.7)
                  : alpha('#14142B', 0.7),
            }}
          >
            Projects are created automatically when you upload your first
            document. This will create the project structure and take you to the
            document upload page.
          </Typography>
          <StyledTextField
            fullWidth
            label="Project Name"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="Enter project name..."
            onKeyPress={(e) => {
              if (e.key === 'Enter' && newProjectName.trim()) {
                createProject();
              }
            }}
            sx={{ mb: 3 }}
            disabled={creating}
          />
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <ActionButton
              onClick={() => setCreateModalOpen(false)}
              disabled={creating}
              sx={{
                backgroundColor: 'transparent',
                color:
                  theme.palette.mode === 'dark'
                    ? alpha('#FFFFFF', 0.7)
                    : alpha('#14142B', 0.7),
                '&:hover': {
                  backgroundColor:
                    theme.palette.mode === 'dark'
                      ? alpha('#FFFFFF', 0.05)
                      : alpha('#14142B', 0.05),
                },
              }}
            >
              Cancel
            </ActionButton>
            <CreateButton
              onClick={createProject}
              disabled={!newProjectName.trim() || creating}
              startIcon={
                creating ? <CircularProgress size={16} /> : <AddIcon />
              }
            >
              {creating ? 'Creating...' : 'Create & Open Project'}
            </CreateButton>
          </Box>
        </Box>
      </StyledModal>
    </PageBackground>
  );
}
