import axios from "axios";

const api = axios.create({
    baseURL: `${import.meta.env.VITE_API_URL}`,
    withCredentials: true,
});

export const test = async () => {
    const response = await api.get(`/test`);
    return response;
};
