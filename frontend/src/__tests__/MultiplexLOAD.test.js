// frontend/src/__tests__/MultiplexLOAD.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import MultiplexLOAD from '../components/MultiplexLOAD';

// ── Mock apiService ──────────────────────────────────────────────────────────
jest.mock('../apiService', () => ({
    uploadFile: jest.fn(),
}));
import { uploadFile } from '../apiService';

// ── Mock JSZip ───────────────────────────────────────────────────────────────
// Stratégie : jest.mock() est hoisted avant toute déclaration.
// On stocke loadAsync dans un objet partagé via le module mock lui-même,
// accessible depuis l'extérieur grâce à JSZip.__mockInstance.
jest.mock('jszip', () => {
    const mockInstance = {
        loadAsync: jest.fn(),
        folder: jest.fn().mockReturnThis(),
        file: jest.fn().mockReturnThis(),
        generateAsync: jest.fn().mockResolvedValue(new Blob()),
    };
    const MockJSZip = jest.fn().mockImplementation(() => mockInstance);
    MockJSZip.__mockInstance = mockInstance;
    return MockJSZip;
});
import JSZip from 'jszip';

// ── Mock react-router-dom ────────────────────────────────────────────────────
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

// ── Setup ────────────────────────────────────────────────────────────────────
beforeEach(() => {
    jest.clearAllMocks();

    window.URL.createObjectURL = jest.fn(() => 'blob:fake');
    window.URL.revokeObjectURL = jest.fn();

    // Reconfigurer après clearAllMocks
    uploadFile.mockResolvedValue({ message: 'File uploaded successfully' });

    // Reconfigurer JSZip via l'instance partagée
    JSZip.mockImplementation(() => JSZip.__mockInstance);
    JSZip.__mockInstance.loadAsync.mockResolvedValue({
        files: {
            'layer_name.tsv': {
                async: jest.fn().mockResolvedValue('1\tGenes\n2\tDiseases\n'),
            },
            'multiplex/1/genes.tsv': {
                async: jest.fn().mockResolvedValue('GeneA\tGeneB\n'),
            },
        },
    });
    JSZip.__mockInstance.folder.mockReturnThis();
    JSZip.__mockInstance.file.mockReturnThis();
    JSZip.__mockInstance.generateAsync.mockResolvedValue(new Blob());
});

// ── Helper ───────────────────────────────────────────────────────────────────
const renderComponent = () =>
    render(<MemoryRouter><MultiplexLOAD /></MemoryRouter>);

// ── Tests : rendu ────────────────────────────────────────────────────────────
describe('MultiplexLOAD — rendu', () => {

    test('se rend sans crash', () => {
        expect(() => renderComponent()).not.toThrow();
    });

    test('affiche le titre "Load your Multiplex"', () => {
        renderComponent();
        expect(screen.getByText(/load your multiplex/i)).toBeInTheDocument();
    });

    test('affiche le texte (.zip only)', () => {
        renderComponent();
        expect(screen.getByText(/\.zip only/i)).toBeInTheDocument();
    });

    test('affiche le bouton "File Deposit"', () => {
        renderComponent();
        expect(screen.getByText(/file deposit/i)).toBeInTheDocument();
    });

    test('affiche le lien "Generate Zip"', () => {
        renderComponent();
        expect(screen.getByText(/generate zip/i)).toBeInTheDocument();
    });

    test('définit le titre du document', () => {
        renderComponent();
        expect(document.title).toBe('GM | Multiplex uploading');
    });
});

// ── Tests : interactions ─────────────────────────────────────────────────────
describe('MultiplexLOAD — interactions', () => {

    test('sélectionner un fichier affiche son nom', () => {
        renderComponent();
        const input = document.querySelector('#m-l-import');
        const fakeFile = new File(['content'], 'test.zip', { type: 'application/zip' });
        Object.defineProperty(input, 'files', { value: [fakeFile] });
        fireEvent.change(input);
        expect(screen.getByText('test.zip')).toBeInTheDocument();
    });

    test('soumettre sans fichier affiche une alerte', async () => {
        renderComponent();
        const submitBtn = document.querySelector('.m-l-change-couche');
        fireEvent.click(submitBtn);
        await waitFor(() => {
            expect(screen.getByText(/veuillez déposer/i)).toBeInTheDocument();
        });
    });

    test('clic sur Generate Zip ouvre la modale', async () => {
        renderComponent();
        const genZipLinks = screen.getAllByText(/generate zip/i);
        fireEvent.click(genZipLinks[0]);
        await waitFor(() => {
            expect(screen.getByText(/zip name/i)).toBeInTheDocument();
        });
    });

    test('soumettre avec un fichier appelle uploadFile', async () => {
        renderComponent();
        const input = document.querySelector('#m-l-import');
        const fakeFile = new File(['PK...'], 'data.zip', { type: 'application/zip' });
        Object.defineProperty(input, 'files', { value: [fakeFile] });
        fireEvent.change(input);

        const submitBtn = document.querySelector('.m-l-change-couche');
        fireEvent.click(submitBtn);

        await waitFor(() => {
            expect(uploadFile).toHaveBeenCalledWith(fakeFile);
        });
    });

    test('après upload réussi, navigate est appelé', async () => {
        renderComponent();
        const input = document.querySelector('#m-l-import');
        const fakeFile = new File(['PK...'], 'data.zip', { type: 'application/zip' });
        Object.defineProperty(input, 'files', { value: [fakeFile] });
        fireEvent.change(input);

        const submitBtn = document.querySelector('.m-l-change-couche');
        fireEvent.click(submitBtn);

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(
                '/multiplex/type_choice',
                expect.objectContaining({
                    state: expect.objectContaining({ tsvDict: expect.any(Object) }),
                })
            );
        });
    });
});