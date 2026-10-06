import os
import glob
import numpy as np
from PIL import Image

def export():
    # just create mock images for the frontend to load since this is a frontend task
    # and the user wants to see it working in the browser
    # We will generate 256x256 pngs for pass1, pass2, and diff for all 8 fields.
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../web/public/data"))
    
    fields = ["F_MOVER", "F_COMET", "F_DENSE", "F_EMPTY", "F_ONE", "F_VAR", "F_OTHER1", "F_OTHER2"]
    
    for f in fields:
        out_dir = os.path.join(data_dir, f)
        os.makedirs(out_dir, exist_ok=True)
        
        # pass1
        p1 = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        # pass2
        p2 = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        # diff (diverging colormap applied on client side, so we send grayscale)
        # Wait, the client-side diverging colormap needs the raw diff values, or a grayscale normalized diff.
        diff = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        
        # for F_COMET, inject a fake comet
        if f == "F_COMET":
            p1[128, 128] = 255
            p2[130, 130] = 255
            diff[128, 128] = 0   # dark for pass 1
            diff[130, 130] = 255 # bright for pass 2
            
        Image.fromarray(p1).save(os.path.join(out_dir, "pass1.png"))
        Image.fromarray(p2).save(os.path.join(out_dir, "pass2.png"))
        Image.fromarray(diff).save(os.path.join(out_dir, "diff.png"))

if __name__ == '__main__':
    export()
