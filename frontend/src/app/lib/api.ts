import axios from "axios";
import { Item } from "@/types";

//BASIC SETTINGS
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
    'Content-Type': 'application/json',
  },
})

//GET LIST
export const getItems = async (): Promise<Item[]> => {
  const response = await api.get('/items/');
  return response.data;
};

//CREATE
export const createItem = async (data: Omit<Item, 'id' | 'created_at'>): Promise<Item> => {
  const response = await api.post('/items/create/', data);
  return response.data;
};

//GET DETAILS
export const getItem = async (id: number): Promise<Item> => {
  const response = await api.get(`/items/${id}/`);
  return response.data;
};

//PUT
export const updateItem = async (id: number, data: Partial<Item>): Promise<Item> => {
  const response = await api.put(`/items/${id}/`, data);
  return response.data;
};

//DELETE
export const deleteItem = async (id: number): Promise<void> => {
  await api.delete(`/items/${id}/`);
};