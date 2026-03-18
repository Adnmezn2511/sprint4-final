// frontend/src/__tests__/LayersSection.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LayersSection from '../components/ZipForm/LayersSection';

const renderComponent = (layers = [], setLayers = jest.fn()) =>
    render(<LayersSection layers={layers} setLayers={setLayers} />);

describe('LayersSection — rendu', () => {

    test('se rend sans crash', () => {
        expect(() => renderComponent()).not.toThrow();
    });

    test('affiche le titre "Multiplex Layer"', () => {
        renderComponent();
        expect(screen.getByText(/multiplex layer/i)).toBeInTheDocument();
    });

    test('affiche le bouton "Add Layer"', () => {
        renderComponent();
        expect(screen.getByRole('button', { name: /add layer/i })).toBeInTheDocument();
    });

    test('affiche les couches passées en props', () => {
        const layers = [
            { id: 1, name: 'Genes', files: [] },
            { id: 2, name: 'Diseases', files: [] },
        ];
        renderComponent(layers);
        expect(screen.getByDisplayValue('Genes')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Diseases')).toBeInTheDocument();
    });

    test('affiche les fichiers d\'une couche', () => {
        const fakeFile = new File(['content'], 'genes.tsv', { type: 'text/plain' });
        const layers = [{ id: 1, name: 'Genes', files: [fakeFile] }];
        renderComponent(layers);
        expect(screen.getByText('genes.tsv')).toBeInTheDocument();
    });
});

describe('LayersSection — interactions', () => {

    test('clic sur Add Layer appelle setLayers avec une nouvelle couche', () => {
        const setLayers = jest.fn();
        renderComponent([], setLayers);
        fireEvent.click(screen.getByRole('button', { name: /add layer/i }));
        expect(setLayers).toHaveBeenCalled();
        const newLayers = setLayers.mock.calls[0][0];
        expect(newLayers).toHaveLength(1);
        expect(newLayers[0]).toMatchObject({ name: '', files: [] });
    });

    test('changer le nom d\'une couche appelle setLayers', () => {
        const setLayers = jest.fn();
        const layers = [{ id: 1, name: '', files: [] }];
        renderComponent(layers, setLayers);
        const input = screen.getByPlaceholderText(/layer name/i);
        fireEvent.change(input, { target: { value: 'Proteins' } });
        expect(setLayers).toHaveBeenCalled();
    });

    test('clic sur Delete Layer appelle setLayers sans la couche', () => {
        const setLayers = jest.fn();
        const layers = [
            { id: 1, name: 'Genes', files: [] },
            { id: 2, name: 'Diseases', files: [] },
        ];
        renderComponent(layers, setLayers);
        const deleteButtons = screen.getAllByRole('button', { name: /delete layer/i });
        fireEvent.click(deleteButtons[0]);
        const result = setLayers.mock.calls[0][0];
        expect(result).toHaveLength(1);
        expect(result[0].name).toBe('Diseases');
    });
});