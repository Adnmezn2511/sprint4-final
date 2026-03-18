// frontend/src/__tests__/GenerateZipForm.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import GenerateZipForm from '../components/ZipForm/GenerateZipForm';

// ── Mocks des props ───────────────────────────────────────────────────────────
const mockOnGenerateZip = jest.fn();
const mockOnClose = jest.fn();

const renderComponent = () =>
    render(
        <GenerateZipForm
            onGenerateZip={mockOnGenerateZip}
            onClose={mockOnClose}
        />
    );

beforeEach(() => {
    jest.clearAllMocks();
});

// ── Tests : rendu ────────────────────────────────────────────────────────────
describe('GenerateZipForm — rendu', () => {

    test('se rend sans crash', () => {
        expect(() => renderComponent()).not.toThrow();
    });

    test('affiche le titre "Generate Zip"', () => {
        renderComponent();
        // Le titre <h3> et le bouton submit contiennent tous les deux "Generate Zip"
        // On cible le <h3> spécifiquement
        expect(screen.getByRole('heading', { name: /generate zip/i })).toBeInTheDocument();
    });

    test('affiche le champ Zip Name', () => {
        renderComponent();
        expect(screen.getByPlaceholderText(/enter the zip name/i)).toBeInTheDocument();
    });

    test('affiche la section Multiplex Layer', () => {
        renderComponent();
        expect(screen.getByText(/multiplex layer/i)).toBeInTheDocument();
    });

    test('affiche la section Bipartite', () => {
        renderComponent();
        // "Bipartite" apparaît dans le <h4> ET dans "Add Bipartite" → on prend le heading
        const elements = screen.getAllByText(/bipartite/i);
        expect(elements.length).toBeGreaterThan(0);
    });

    test('affiche le bouton "Add Layer"', () => {
        renderComponent();
        expect(screen.getByRole('button', { name: /add layer/i })).toBeInTheDocument();
    });

    test('affiche le bouton "Add Bipartite"', () => {
        renderComponent();
        expect(screen.getByRole('button', { name: /add bipartite/i })).toBeInTheDocument();
    });

    test('affiche le bouton de soumission Generate Zip', () => {
        renderComponent();
        expect(screen.getByRole('button', { name: /generate zip/i })).toBeInTheDocument();
    });

    test('affiche le bouton de fermeture ×', () => {
        renderComponent();
        expect(screen.getByText('×')).toBeInTheDocument();
    });
});

// ── Tests : interactions ─────────────────────────────────────────────────────
describe('GenerateZipForm — interactions', () => {

    test('clic sur × appelle onClose', () => {
        renderComponent();
        fireEvent.click(screen.getByText('×'));
        expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    test('soumettre sans nom de zip affiche une erreur', () => {
        renderComponent();
        fireEvent.click(screen.getByRole('button', { name: /generate zip/i }));
        expect(screen.getByText(/please enter the zip name/i)).toBeInTheDocument();
    });

    test('soumettre sans layer affiche une erreur', () => {
        renderComponent();
        // Remplir le zip name
        fireEvent.change(screen.getByPlaceholderText(/enter the zip name/i), {
            target: { value: 'my_multiplex' },
        });
        fireEvent.click(screen.getByRole('button', { name: /generate zip/i }));
        expect(screen.getByText(/please add at least one layer/i)).toBeInTheDocument();
    });

    test('remplir le champ zip name met à jour la valeur', () => {
        renderComponent();
        const input = screen.getByPlaceholderText(/enter the zip name/i);
        fireEvent.change(input, { target: { value: 'test_zip' } });
        expect(input.value).toBe('test_zip');
    });

    test('clic sur "Add Layer" ajoute un layer dans la liste', () => {
        renderComponent();
        fireEvent.click(screen.getByRole('button', { name: /add layer/i }));
        // Un champ Layer Name doit apparaître
        expect(screen.getByPlaceholderText(/layer name/i)).toBeInTheDocument();
    });
});