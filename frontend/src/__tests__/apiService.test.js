// frontend/src/__tests__/apiService.test.js
import { GraphJson, testapi, uploadFile } from '../apiService';

global.fetch = jest.fn();

beforeEach(() => {
    fetch.mockClear();
    process.env.REACT_APP_API_URL = 'http://localhost:8000/';
});

describe('apiService — GraphJson', () => {

    test('appelle fetch avec la bonne URL et méthode POST', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: [], layout: {} }),
        });
        await GraphJson(['GeneA'], 2, 10, 0.7, 'alice', 'Test');
        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining('graph/'),
            expect.objectContaining({ method: 'POST' })
        );
    });

    test('envoie les seeds dans le body', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({}),
        });
        await GraphJson(['GeneA', 'GeneB'], 3, 5, 0.5, 'bob', 'MyGraph');
        const body = JSON.parse(fetch.mock.calls[0][1].body);
        expect(body.seeds).toEqual(['GeneA', 'GeneB']);
        expect(body.steps).toBe(3);
        expect(body.top).toBe(5);
        expect(body.restart).toBe(0.5);
        expect(body.user).toBe('bob');
        expect(body.title).toBe('MyGraph');
    });

    test('retourne null et log en cas d\'erreur réseau', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        fetch.mockRejectedValueOnce(new Error('Network error'));
        const result = await GraphJson(['G'], 1, 5, 0.3, 'u', 't');
        expect(result).toBeUndefined();
        consoleSpy.mockRestore();
    });

    test('retourne les données JSON en cas de succès', async () => {
        const mockData = { data: [{ type: 'scatter' }], layout: {} };
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockData,
        });
        const result = await GraphJson(['G'], 1, 5, 0.3, 'u', 't');
        expect(result).toEqual(mockData);
    });
});

describe('apiService — testapi', () => {

    test('appelle l\'endpoint /test', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ test: 'Hello from Django!' }),
        });
        await testapi();
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('test'));
    });

    test('retourne la valeur de test.test', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ test: 'Hello from Django!' }),
        });
        const result = await testapi();
        expect(result).toBe('Hello from Django!');
    });

    test('gère les erreurs réseau sans crash', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        fetch.mockRejectedValueOnce(new Error('Network error'));
        const result = await testapi();
        expect(result).toBeUndefined();
        consoleSpy.mockRestore();
    });
});

describe('apiService — uploadFile', () => {

    test('appelle fetch avec FormData et méthode POST', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ message: 'File uploaded successfully' }),
        });
        const fakeFile = new File(['content'], 'test.zip', { type: 'application/zip' });
        await uploadFile(fakeFile);
        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining('upload-zip'),
            expect.objectContaining({ method: 'POST' })
        );
    });

    test('envoie le fichier dans le body FormData', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ message: 'OK' }),
        });
        const fakeFile = new File(['zip content'], 'data.zip', { type: 'application/zip' });
        await uploadFile(fakeFile);
        const callArgs = fetch.mock.calls[0];
        const body = callArgs[1].body;
        expect(body).toBeInstanceOf(FormData);
    });

    test('lève une erreur si le serveur répond avec erreur', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            statusText: 'Bad Request',
        });
        const fakeFile = new File(['bad'], 'bad.zip');
        await expect(uploadFile(fakeFile)).rejects.toThrow();
    });

    test('retourne la réponse JSON en cas de succès', async () => {
        const mockResponse = { message: 'File uploaded successfully' };
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockResponse,
        });
        const fakeFile = new File(['ok'], 'ok.zip');
        const result = await uploadFile(fakeFile);
        expect(result).toEqual(mockResponse);
    });
});