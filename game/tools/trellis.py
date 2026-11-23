import sys, shutil
from gradio_client import Client, handle_file
img, out = sys.argv[1], sys.argv[2]
c = Client('trellis-community/TRELLIS')
try: c.predict(api_name='/start_session')
except Exception as e: print('start_session', e)
pre = c.predict(image=handle_file(img), api_name='/preprocess_image')
print('pre', pre)
res = c.predict(image=handle_file(pre), multiimages=[], seed=7, ss_guidance_strength=7.5, ss_sampling_steps=12,
                slat_guidance_strength=3.0, slat_sampling_steps=12, multiimage_algo='stochastic',
                mesh_simplify=0.9, texture_size=1024, api_name='/generate_and_extract_glb')
print('res', res)
glb = res[2] if isinstance(res[2], str) else (res[2] or {}).get('value')
shutil.copy(glb, out); print('OK', out)
