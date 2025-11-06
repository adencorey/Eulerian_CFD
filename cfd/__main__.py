import pstats
import cProfile

from cfd.main import main
import cfd.utilities.logger as log

if __name__ == "__main__":
    
    log.init()
    profile = True
    if profile:
        cProfile.run("main()", "cfd_profile.prof")
        stats = pstats.Stats("cfd_profile.prof")
        stats.sort_stats("cumtime").reverse_order().print_stats()
    else:
        main()