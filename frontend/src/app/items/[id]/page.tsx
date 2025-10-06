import ItemForm from '@/components/ItemForm';
import { getItem, deleteItem } from '@/app/lib/api';
import { Item } from '@/types';
import { redirect } from 'next/navigation';

interface Params {
  params: { id: string };
}

export default async function ItemPage({ params }: Params) {
  const id = parseInt(params.id);
  let item: Item | null = null;
  try {
    item = await getItem(id);
  } catch {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <p className="text-gray-600 text-lg">Item not found</p>
      </div>
    );
  }

  async function handleDelete() {
    'use server';
    await deleteItem(id);
    redirect('/');
  }

  async function handleSuccess() {
    'use server';
    redirect('/');
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Item Details</h1>
        <ItemForm item={item} onSuccess={handleSuccess} />
        
        <div className="mt-6 pt-6 border-t border-gray-200">
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