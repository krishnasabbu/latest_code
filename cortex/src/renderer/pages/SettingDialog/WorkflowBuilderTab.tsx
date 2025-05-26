import React, { useState } from 'react';
import {
  DndContext,
  useDraggable,
  useDroppable,
  DragEndEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCenter,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import {
  Box,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
} from '@mui/material';

import { Delete as DeleteIcon, Settings as SettingsIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { Settings, Theme, Workflow, WorkflowProvider } from '../../../shared/types';
import { settingsAtom } from '@/stores/atoms';
import { useAtom } from 'jotai';
import { useTheme } from '@mui/material/styles';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize'

const generateUniqueId = (() => {
  let count = 0;
  return () => `step-${++count}`;
})();

function DraggableBox({ provider }: { provider: any }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: provider.id,
    data: { provider }, // <-- fix: wrap provider inside data object for drag event
  });

  const style = {
    transform: transform ? CSS.Translate.toString(transform) : undefined,
    cursor: 'grab',
    userSelect: 'none',
  };

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      style={{
        ...style,
        padding: '8px',
        border: '1px solid #999',
        borderRadius: 4,
        marginBottom: 8,
        background: 'transparent',
      }}
    >
      {provider.label}
    </div>
  );
}

function SortableWorkflowItem({
  step,
  index,
  onDeleteStep,
  onOpenSettings,
}: {
  step: any;
  index: number;
  onDeleteStep: (stepId: string) => void;
  onOpenSettings: (step: any) => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: step.id });

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  return (
    <Box
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      sx={{
        ...style,
        p: 1,
        mb: 1,
        border: '1px solid #999',
        borderRadius: 1,
        backgroundColor: 'background.paper',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <span>
        Step {index + 1}: {step.label}
      </span>
      <Box>
        <IconButton size="small" color="primary" onClick={() => onOpenSettings(step)}>
          <SettingsIcon />
        </IconButton>
        <IconButton size="small" color="error" onClick={() => onDeleteStep(step.id)}>
          <DeleteIcon />
        </IconButton>
      </Box>
    </Box>
  );
}

function CanvasDropZone({ children }: { children: React.ReactNode }) {
  const { setNodeRef } = useDroppable({ id: 'canvas-drop-zone' });

  return (
    <Box
      ref={setNodeRef}
      height="400px"
      border="2px dashed #aaa"
      borderRadius={2}
      p={2}
      overflow="auto"
      bgcolor="background.default"
    >
      {children}
    </Box>
  );
}

export default function WorkflowBuilderTab(props: {
  settingsEdit: Settings;
  setSettingsEdit: (settings: Settings) => void;
  changeModeWithPreview: (newMode: Theme) => void;
}) {
  const { settingsEdit, setSettingsEdit } = props;
  const { t } = useTranslation();
  const theme = useTheme();
  const [globalSettings] = useAtom(settingsAtom);
  const [workflowProviders, setWorkflowProviders] = useState<WorkflowProvider[]>(settingsEdit.workflowProviders || []);
  const [workflowProvider, setWorkflowProvider] = useState<WorkflowProvider>();
  const [workflow, setWorkflow] = useState<Workflow[]>([]);
  const [saved, setSaved] = useState(false);

  const sensors = useSensors(useSensor(PointerSensor));

  const availableProviders = settingsEdit.customProviders.map((provider) => ({
    id: provider.id,
    label: provider.name,
    api: provider.api,
  }));

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeStep, setActiveStep] = useState<any | null>(null);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [selectedTool, setSelectedTool] = useState('');
  const [workflowName, setWorkflowName] = useState(settingsEdit.name || '');

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    // Correctly access draggable data:
    const draggedProvider = active.data?.current?.provider;

    // Dropped on canvas: add new step
    if (over.id === 'canvas-drop-zone' && draggedProvider) {
      const newStep = {
        ...draggedProvider,
        id: generateUniqueId(),
        originalProviderId: draggedProvider.id,
        api: draggedProvider.api,
        config: {},
      };
      setWorkflow((prev) => [...prev, newStep]);
      return;
    }

    // Reorder steps inside canvas
    if (
      String(active.id).startsWith('step-') &&
      String(over.id).startsWith('step-') &&
      active.id !== over.id
    ) {
      const oldIndex = workflow.findIndex((w) => w.id === active.id);
      const newIndex = workflow.findIndex((w) => w.id === over.id);
      setWorkflow((items) => arrayMove(items, oldIndex, newIndex));
    }
  };

  const onDeleteStep = (stepId: string) => {
    setWorkflow((prev) => prev.filter((step) => step.id !== stepId));
  };

  const onOpenSettings = (step: any) => {
    setActiveStep(step);
    if (step.config) {
      setSystemPrompt(step.config.systemPrompt || '');
      setSelectedTool(step.config.selectedTool || '');
    } else {
      setSystemPrompt('');
      setSelectedTool('');
    }
    setSettingsOpen(true);
  };

  const handleSettingsSave = () => {
    if (!activeStep) return;
    setWorkflow((prev) =>
      prev.map((step) => {
        if (step.id === activeStep.id) {
          return {
            ...step,
            config: {
              systemPrompt: systemPrompt.trim(),
              selectedTool: selectedTool,
            },
          };
        }
        return step;
      })
    );
    setSettingsOpen(false);
    setActiveStep(null);
    setSystemPrompt('');
    setSelectedTool('');
  };

  const handleSettingsClose = () => {
    setSettingsOpen(false);
    setActiveStep(null);
    setSystemPrompt('');
    setSelectedTool('');
  };

  const toolsForActiveStep = (() => {
    if (!activeStep) return [];
    const originalProviderId = activeStep.originalProviderId || activeStep.id;
    const foundProvider = settingsEdit.customProviders.find((p) => p.id === originalProviderId);
    return foundProvider?.tools || ['test'];
  })();

  const isAIProvider = (() => {
    if (!activeStep) return false;
    const originalProviderId = activeStep.originalProviderId || activeStep.id;
    const foundProvider = settingsEdit.customProviders.find((p) => p.id === originalProviderId);
    return foundProvider?.api === 'openai';
  })();

  const handleSave = () => {

    if (!workflowProvider) return;

    const updatedProvider: WorkflowProvider = {
        ...workflowProvider,
        definition: workflow,
    };

    setWorkflowProviders((prev) => {
        const existingIndex = prev.findIndex(p => p.id === updatedProvider.id);
        if (existingIndex !== -1) {
        // Update existing
        const copy = [...prev];
        copy[existingIndex] = updatedProvider;
        return copy;
        } else {
        // Add new
        return [...prev, updatedProvider];
        }
    });

    setSettingsEdit({
        ...settingsEdit,
        workflowProviders: workflowProviders
    })

    // Optional: Reset for next creation
    setWorkflow([]);
    setWorkflowProvider(undefined);
  };

  const handleWorkflowNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value
    setWorkflowProvider((prev) => prev ? { ...prev, name: newName } : { id: generateUniqueId(), name: newName, definition: [] });
  };

  const handleSelectWorkflowProvider = (provider: WorkflowProvider) => {
    setWorkflowProvider(provider);
    setWorkflow(provider.definition || []);
  };

  return (
    <>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <Box display="flex" height="100%" p={2}>
            <Box
              width="30%"
              pr={2}
              borderRight={`1px solid ${theme.palette.divider}`}
              bgcolor={theme.palette.background.paper}
              color={theme.palette.text.primary}
              borderRadius={2}
            >
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                    {t('WorkFlows')}
                </Typography>

                {workflowProviders.map((p) => (
                    <Button key={p.id} 
                            variant="contained" 
                            color="primary"
                            onClick={() => handleSelectWorkflowProvider(p)}>
                        <DashboardCustomizeIcon /> {p.name}
                    </Button>
                ))}

                <Divider sx={{ my: 0.5 }} />
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                    {t('Custom Providers')}
                </Typography>

                {availableProviders.map((p) => (
                    <DraggableBox key={p.id} provider={p} />
                ))}
            </Box>

            <Box flex={1} pl={2}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                {t('Workflow Builder')}
              </Typography>
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="Workflow Name"
                  value={workflowProvider?.name || ''}
                  onChange={handleWorkflowNameChange}
                  placeholder="Enter a name for this workflow"
                />
              </Box>
              <CanvasDropZone>
                <SortableContext items={workflow.map((w) => w.id)} strategy={verticalListSortingStrategy}>
                  {workflow.map((step, idx) => (
                    <SortableWorkflowItem
                      key={step.id}
                      step={step}
                      index={idx}
                      onDeleteStep={onDeleteStep}
                      onOpenSettings={onOpenSettings}
                    />
                  ))}
                </SortableContext>
              </CanvasDropZone>

              <Box mt={2} textAlign="right">
                <Button variant="contained" color="primary" onClick={handleSave} disabled={!workflowName || workflow.length === 0}>
                  Save Workflow
                </Button>
              </Box>
            </Box>
          </Box>

          {/* Settings Dialog */}
          <Dialog open={settingsOpen} onClose={handleSettingsClose} maxWidth="sm" fullWidth>
            <DialogTitle>{t('Configure Step Settings')}</DialogTitle>
            <DialogContent dividers>
            {isAIProvider ? (
                <TextField
                fullWidth
                multiline
                minRows={3}
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder={t('System prompt')}
                />
            ) : (
                <FormControl fullWidth>
                <InputLabel id="tool-select-label">{t('Select Tool')}</InputLabel>
                <Select
                    labelId="tool-select-label"
                    value={selectedTool}
                    onChange={(e) => setSelectedTool(e.target.value)}
                >
                    {toolsForActiveStep.map((tool) => (
                    <MenuItem key={tool} value={tool}>
                        {tool}
                    </MenuItem>
                    ))}
                </Select>
                </FormControl>
            )}
            </DialogContent>
            <DialogActions>
            <Button onClick={handleSettingsClose}>{t('Cancel')}</Button>
            <Button variant="contained" onClick={handleSettingsSave}>
                {t('Save')}
            </Button>
            </DialogActions>
        </Dialog>
        </DndContext>
    </>
  );
}
