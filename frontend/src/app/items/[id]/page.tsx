import ItemForm from '@/components/ItemForm';
import { getItem, deleteItem } from '@/lib/api';
import { Item } from '@/types';
import { redirect } from 'next/navigation';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function ItemDetailPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params;
  const itemId = parseInt(id);
  
  let item: Item | null = null;
  
  try {
    item = await getItem(itemId);
  } catch {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <p className="text-gray-600 text-lg">Item not found</p>
      </div>
    );
  }

  async function handleDelete() {
    'use server';
    await deleteItem(itemId);
    redirect('/');  
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Edit Item</h1>
        <ItemForm item={item} />
        
        <div className="mt-6 pt-6 border-gray-200">
          <form action={handleDelete}>
            <button 
              type="submit" 
              className="bg-red-500 hover:bg-red-600 text-white font-medium px-6 py-2.5 rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md"
            >
              Delete Item
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}