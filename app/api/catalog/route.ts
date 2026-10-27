import {searchCatalog,genres,catalogSize} from '@/lib/recommend';
export async function GET(request:Request){const q=new URL(request.url).searchParams.get('q')||'';if(q.length>100)return Response.json({error:'Search must be under 100 characters.'},{status:400});return Response.json({movies:searchCatalog(q),genres,catalogSize},{headers:{'Cache-Control':'public, max-age=3600'}});}
