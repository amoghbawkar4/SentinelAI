import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import DocumentIngestionPage from './DocumentIngestionPage';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

vi.mock('../utils/api', () => ({
  default: {
    post: vi.fn(),
  },
}));

describe('DocumentIngestionPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', email: 'hr@company.com', role_name: 'HR' },
      logout: vi.fn(),
      loading: false,
      login: vi.fn(),
      register: vi.fn(),
    } as any);
  });

  it('shows selected file details and submits a valid upload request', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { id: 'doc-123', original_filename: 'Compensation_Policy.pdf', processing_status: 'RECEIVED', allowed_roles: ['HR'] } });

    render(
      <MemoryRouter>
        <DocumentIngestionPage />
      </MemoryRouter>,
    );

    const file = new File(['pdf-data'], 'Compensation_Policy.pdf', { type: 'application/pdf' });
    fireEvent.change(screen.getByLabelText(/select document/i), { target: { files: [file] } });

    expect(screen.getByText('Compensation_Policy.pdf')).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('HR'));
    fireEvent.click(screen.getByRole('button', { name: /secure & ingest/i }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/documents/upload', expect.any(FormData), expect.any(Object));
    });

    expect(screen.getByText(/document received successfully/i)).toBeInTheDocument();
  });

  it('rejects unsupported files before submission', () => {
    render(
      <MemoryRouter>
        <DocumentIngestionPage />
      </MemoryRouter>,
    );

    const file = new File(['fake'], 'notes.exe', { type: 'application/x-msdownload' });
    fireEvent.change(screen.getByLabelText(/select document/i), { target: { files: [file] } });

    expect(screen.getByText(/unsupported file type/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /secure & ingest/i })).toBeDisabled();
  });
});
