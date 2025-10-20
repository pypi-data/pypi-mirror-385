<img src='images/goal.png'/>
MSA by ML researchers for ML researchers --️ in pytorch/cuda ❤️

```
pip install sseqs
wget https://foldify.org/uniref_bfd_mgy_cf.xbit 
```

```
from sseqs import msa
msa("HPETLVKVKDAEDQLGARVGYIELDLNSGKILE...", "msa.a3m")
```

No need for <a href="https://instances.vantage.sh/aws/ec2/x2gd.16xlarge?currency=USD">$5h/h</a> 1000GB RAM server.   Developed on/for desktop with rtx4090+128GB RAM for $0.3/h on <a href="https://cloud.vast.ai/">vast.ai</a>. 


# limitations
- no protein pairing 
- sequence length < 1000 (working on 2048)
- 128gb RAM (working on 64GB w/ compression) 
- server.py supporting Boltz2 MSA-server (adding soon)
- no <16GB approximate version (yet)
- no evals (working on runs'n'poses + antibody)
