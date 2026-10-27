import metrics from '@/lib/metrics.json';
export async function GET(){return Response.json(metrics,{headers:{'Cache-Control':'no-store'}});}
